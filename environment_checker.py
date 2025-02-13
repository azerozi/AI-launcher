import sys
import subprocess
import pkg_resources
import platform
import shutil
import os

class EnvironmentManager:
    def __init__(self):
        self.required_python_version = (3, 11, 9)
        # 只保留核心必需的包
        self.required_packages = {
            'torch': '2.0.0',
            'transformers': '4.30.0',
            'tkinter': None,
            'numpy': '1.24.0',
        }
        # 将其他包移到可选包
        self.optional_packages = {
            'pandas': '1.5.0',
            'scipy': '1.9.0',
            'PIL': '9.0.0',
            'matplotlib': '3.5.0',
            'notebook': '6.0.0',
            'IPython': '8.0.0'
        }
        self.missing_packages = []
        self.python_ok = False
        self.cuda_ok = False
        
    def check_python_version(self):
        """检查Python版本"""
        current_version = sys.version_info[:3]
        version_str = '.'.join(map(str, current_version))
        
        if current_version >= self.required_python_version:
            return True, f"Python版本 {version_str} 符合要求"
        else:
            required_str = '.'.join(map(str, self.required_python_version))
            return False, f"Python版本 {version_str} 不满足要求，需要 {required_str} 或更高版本"
    
    def check_cuda(self):
        """检查CUDA环境"""
        try:
            import torch
            if torch.cuda.is_available():
                device_name = torch.cuda.get_device_name(0)
                cuda_version = torch.version.cuda
                return True, f"CUDA可用: {device_name} (CUDA {cuda_version})"
            else:
                # 检查是否安装了CUDA版本的PyTorch
                if not hasattr(torch, '__cuda_version__'):
                    return False, "PyTorch未安装CUDA版本，请重新安装"
                else:
                    return False, f"CUDA不可用，请检查NVIDIA驱动是否正确安装"
        except ImportError:
            return False, "PyTorch未安装"
        except Exception as e:
            return False, f"CUDA检查出错: {str(e)}"
    
    def check_dependencies(self):
        """检查依赖包"""
        results = []
        self.missing_packages = []
        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        
        # 检查 PyTorch
        try:
            import torch
            version = torch.__version__
            if torch.cuda.is_available():
                results.append((True, f"PyTorch {version} (CUDA) 已安装"))
            else:
                results.append((True, f"PyTorch {version} (CPU) 已安装"))
        except ImportError:
            results.append((False, "PyTorch 未安装"))
            self.missing_packages.append("torch")
        
        # 检查必需包
        for package, required_version in self.required_packages.items():
            # 跳过已检查的 PyTorch
            if package == 'torch':
                continue
            
            if package == 'tkinter':
                try:
                    import tkinter
                    results.append((True, f"{package} 已安装"))
                except ImportError:
                    results.append((False, f"{package} 未安装"))
                    self.missing_packages.append(package)
                continue
            
            # 检查其他必需包
            if package in installed_packages:
                installed_version = installed_packages[package]
                if required_version and pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(required_version):
                    results.append((False, f"{package} 版本 {installed_version} 过低，需要 {required_version} 或更高"))
                    self.missing_packages.append(f"{package}>={required_version}")
                else:
                    results.append((True, f"{package} 版本 {installed_version} 已安装"))
            else:
                results.append((False, f"{package} 未安装"))
                if required_version:
                    self.missing_packages.append(f"{package}>={required_version}")
                else:
                    self.missing_packages.append(package)
        
        return results
    
    def check_disk_space(self):
        """检查磁盘空间"""
        required_space = 5 * 1024 * 1024 * 1024  # 降低到5GB，因为排除了一些大型依赖
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            total, used, free = shutil.disk_usage(current_dir)
            free_gb = free / (1024 * 1024 * 1024)
            
            if free > required_space:
                return True, f"可用磁盘空间: {free_gb:.1f}GB，空间充足"
            else:
                return False, f"可用磁盘空间: {free_gb:.1f}GB，建议至少预留5GB空间"
        except Exception as e:
            return False, f"无法检查磁盘空间: {str(e)}"
    
    def install_dependencies(self, callback=None):
        """安装缺失的依赖"""
        if not self.missing_packages:
            return True, "没有需要安装的依赖"
            
        try:
            # 先安装 PyTorch
            for pkg in self.missing_packages:
                if pkg.startswith('torch>='):
                    if callback:
                        callback("正在从官方源安装 PyTorch (CUDA版本)...")
                    
                    # PyTorch 从官方源安装 CUDA 版本
                    torch_cmd = [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "torch==2.2.1",
                        "torchvision==0.17.1",
                        "torchaudio==2.2.1",
                        "--index-url",
                        "https://download.pytorch.org/whl/cu121",
                        "--no-cache-dir"
                    ]
                    
                    process = subprocess.Popen(
                        torch_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output and callback:
                            callback(output.strip())
                    
                    if process.returncode != 0:
                        error = process.stderr.read()
                        if callback:
                            callback(f"PyTorch安装失败: {error}")
                        return False, "PyTorch安装失败，请手动安装"
                    break
            
            # 安装其他包（使用清华源）
            other_packages = [pkg for pkg in self.missing_packages if not pkg.startswith('torch>=')]
            if other_packages:
                if callback:
                    callback("正在从清华源安装其他依赖...")
                
                cmd = [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-i",
                    "https://pypi.tuna.tsinghua.edu.cn/simple",
                    "--trusted-host",
                    "pypi.tuna.tsinghua.edu.cn"
                ] + other_packages
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output and callback:
                        callback(output.strip())
                
                if process.returncode != 0:
                    error = process.stderr.read()
                    if callback:
                        callback(f"依赖安装失败: {error}")
                    return False, "依赖安装失败，请手动安装"
            
            self.missing_packages = []
            return True, "依赖安装完成"
                
        except Exception as e:
            return False, f"安装出错: {str(e)}"
    
    def check_optional_dependencies(self):
        """检查可选依赖包"""
        results = []
        for package, required_version in self.optional_packages.items():
            try:
                import pkg_resources
                installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
                
                if package in installed_packages:
                    installed_version = installed_packages[package]
                    if required_version and pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(required_version):
                        results.append((False, f"{package} 版本 {installed_version} 过低，建议 {required_version} 或更高"))
                    else:
                        results.append((True, f"{package} 版本 {installed_version} 已安装"))
                else:
                    results.append((False, f"{package} 未安装 (可选)"))
            except Exception as e:
                results.append((False, f"{package} 检查出错: {str(e)}"))
                
        return results 