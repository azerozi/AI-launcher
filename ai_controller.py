from typing import List
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

class AIController:
    def __init__(self, model_path: str):
        self.model_path = model_path  # 添加这一行来保存模型路径
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, 
            trust_remote_code=True,
            device_map="auto",
            torch_dtype=torch.float16
        )
        self.chat_history = []  # 确保初始化为空列表
        self.clear_history()    # 显式清空历史记录
        # 检测模型是否支持思考过程
        self.supports_thinking = self._check_thinking_support()
    
    def _check_thinking_support(self) -> bool:
        """检查模型是否支持思考过程输出"""
        try:
            # 构建一个简单的测试消息
            messages = [{"role": "user", "content": "你好"}]
            input_text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # 如果模板中包含 <think> 标签，说明支持思考过程
            return "<think>" in input_text
        except:
            return False
    
    def chat(self, user_input: str, system_prompt: str = None) -> tuple[str, str]:
        try:
            # 构建输入格式
            messages = []
            
            # 确保系统提示词只在对话开始时添加一次
            if system_prompt and not self.chat_history:
                messages.append({"role": "system", "content": system_prompt})
            
            # 添加历史对话
            for hist in self.chat_history:
                messages.extend([
                    {"role": "user", "content": hist[0]},
                    {"role": "assistant", "content": hist[1]}
                ])
            
            # 添加当前用户输入
            messages.append({"role": "user", "content": user_input})
            
            # 将消息转换为模型输入格式
            input_text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # 编码输入
            inputs = self.tokenizer(input_text, return_tensors="pt").to(self.model.device)
            
            # 生成回复
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=2048,
                do_sample=True,
                temperature=0.7,
                top_p=0.8,
                repetition_penalty=1.1
            )
            
            # 解码输出
            response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            
            # 分离思考过程和回复
            parts = response.split("</think>", 1)
            if len(parts) == 2:
                thought, response = parts
                # 清理思考过程中可能的HTML标签
                thought = thought.strip().replace("<think>", "").strip()
            else:
                # 如果没有找到分隔符，假设整个响应都是正式回复
                thought = ""
                response = response.strip()
            
            # 如果response为空，说明分割可能有问题
            if not response.strip():
                response = parts[0].strip()
                thought = ""
            
            # 更新历史记录 (只保存正式回复)
            self.chat_history.append((user_input, response))
            return thought, response
            
        except Exception as e:
            raise Exception(f"模型响应出错：{str(e)}")
    
    def clear_history(self):
        self.chat_history.clear()
        
    @staticmethod
    def get_available_models(models_dir: str = "models") -> List[str]:
        """获取models文件夹中的所有可用模型"""
        if not os.path.exists(models_dir):
            return []
        return [d for d in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, d))]
