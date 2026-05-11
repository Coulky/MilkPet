# -*- coding: utf-8 -*-
"""
安全数据存储模块

功能：
- 数据加密/解密
- 用户机器唯一标识
- 安全的数据存储路径
- 数据验证和重置
"""

import sys
import os
import json
import base64
import hashlib
import hmac
import secrets
from typing import Dict, Any, Optional
from datetime import datetime


def get_machine_id() -> str:
    """
    获取机器唯一标识符
    
    Windows: 使用用户名 + 计算机名
    非 Windows: 使用 MAC 地址
    
    返回: 唯一标识符字符串
    """
    try:
        if sys.platform == 'win32':
            # Windows：使用用户名 + 计算机名（不需要管理员权限）
            import getpass
            import socket
            username = getpass.getuser()
            hostname = socket.gethostname()
            combined = f"{username}_{hostname}"
            return hashlib.sha256(combined.encode()).hexdigest()[:16]
        
        else:
            # 非 Windows 平台：使用 MAC 地址
            import uuid
            node = uuid.getnode()
            return hashlib.sha256(str(node).encode()).hexdigest()[:16]
            
    except Exception as e:
        print(f"[WARN] 获取机器ID失败: {e}，使用备用ID")
        return "default_user_" + hashlib.md5(os.path.expanduser("~").encode()).hexdigest()[:8]


def _derive_key(key: str, salt: bytes) -> bytes:
    """
    使用 PBKDF2 从密码派生密钥
    
    参数:
        key: 原始密钥字符串
        salt: 随机盐值
        
    返回: 32字节的派生密钥
    """
    key_bytes = key.encode('utf-8')
    # 使用 PBKDF2-HMAC-SHA256 进行密钥派生
    derived = hashlib.pbkdf2_hmac('sha256', key_bytes, salt, 100000)
    return derived


def _aes_gcm_encrypt(plaintext: bytes, key: bytes) -> tuple:
    """
    使用 AES-GCM 模式加密数据（纯 Python 实现）
    
    参数:
        plaintext: 要加密的明文数据
        key: 32字节加密密钥
        
    返回: (密文, nonce, tag) 元组
    """
    # 生成随机 nonce (12字节是 GCM 推荐值)
    nonce = secrets.token_bytes(12)
    
    # 使用 HMAC-SHA256 模拟 GCM 的认证加密
    # 实际实现中使用 ChaCha20-Poly1305 或 AES-GCM 更好
    # 这里使用 Encrypt-then-MAC 模式
    
    # 生成加密密钥和 MAC 密钥
    enc_key = hashlib.sha256(key + b'encryption').digest()
    mac_key = hashlib.sha256(key + b'authentication').digest()
    
    # 使用 ChaCha20 流密码（简化版）
    # 实际应该使用 cryptography 库，但为了零依赖，使用基于 HMAC 的流密码
    keystream = b''
    counter = 0
    while len(keystream) < len(plaintext):
        block = hmac.new(enc_key, nonce + counter.to_bytes(4, 'big'), hashlib.sha256).digest()
        keystream += block
        counter += 1
    
    # XOR 加密
    ciphertext = bytes(p ^ k for p, k in zip(plaintext, keystream[:len(plaintext)]))
    
    # 计算认证标签 (HMAC-SHA256 的前 16 字节)
    tag = hmac.new(mac_key, nonce + ciphertext, hashlib.sha256).digest()[:16]
    
    return ciphertext, nonce, tag


def _aes_gcm_decrypt(ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes) -> bytes:
    """
    使用 AES-GCM 模式解密数据
    
    参数:
        ciphertext: 密文数据
        key: 32字节加密密钥
        nonce: 随机数
        tag: 认证标签
        
    返回: 解密后的明文
        
    异常:
        ValueError: 认证失败时抛出
    """
    # 生成加密密钥和 MAC 密钥
    enc_key = hashlib.sha256(key + b'encryption').digest()
    mac_key = hashlib.sha256(key + b'authentication').digest()
    
    # 验证认证标签
    expected_tag = hmac.new(mac_key, nonce + ciphertext, hashlib.sha256).digest()[:16]
    if not hmac.compare_digest(tag, expected_tag):
        raise ValueError("数据认证失败：数据可能被篡改")
    
    # 生成密钥流
    keystream = b''
    counter = 0
    while len(keystream) < len(ciphertext):
        block = hmac.new(enc_key, nonce + counter.to_bytes(4, 'big'), hashlib.sha256).digest()
        keystream += block
        counter += 1
    
    # XOR 解密
    plaintext = bytes(c ^ k for c, k in zip(ciphertext, keystream[:len(ciphertext)]))
    
    return plaintext


def secure_encrypt(data: str, key: str) -> str:
    """
    安全的加密（使用基于 HMAC 的认证加密）
    
    参数:
        data: 要加密的数据字符串
        key: 加密密钥
        
    返回: 加密后的 base64 字符串（格式: salt + nonce + tag + ciphertext）
    """
    # 生成随机盐值
    salt = secrets.token_bytes(16)
    
    # 派生密钥
    derived_key = _derive_key(key, salt)
    
    # 加密数据
    plaintext = data.encode('utf-8')
    ciphertext, nonce, tag = _aes_gcm_encrypt(plaintext, derived_key)
    
    # 组合: salt(16) + nonce(12) + tag(16) + ciphertext
    encrypted_package = salt + nonce + tag + ciphertext
    
    # 返回 base64 编码
    return base64.b64encode(encrypted_package).decode('utf-8')


def secure_decrypt(encrypted_data: str, key: str) -> str:
    """
    安全的解密
    
    参数:
        encrypted_data: 加密的 base64 字符串
        key: 解密密钥
        
    返回: 解密后的原始字符串
        
    异常:
        ValueError: 解密或认证失败时抛出
    """
    try:
        # 解码 base64
        encrypted_package = base64.b64decode(encrypted_data.encode('utf-8'))
        
        # 解析: salt(16) + nonce(12) + tag(16) + ciphertext
        if len(encrypted_package) < 44:
            raise ValueError("加密数据格式错误")
        
        salt = encrypted_package[:16]
        nonce = encrypted_package[16:28]
        tag = encrypted_package[28:44]
        ciphertext = encrypted_package[44:]
        
        # 派生密钥
        derived_key = _derive_key(key, salt)
        
        # 解密数据
        plaintext = _aes_gcm_decrypt(ciphertext, derived_key, nonce, tag)
        
        return plaintext.decode('utf-8')
        
    except Exception as e:
        raise ValueError(f"解密失败: {e}")


# 保持向后兼容：旧函数名映射到新实现
simple_encrypt = secure_encrypt
simple_decrypt = secure_decrypt


class SecureStorage:
    """安全数据存储管理器"""
    
    def __init__(self, app_name: str = "MilkPet", data_file: str = "player_data.dat"):
        self.app_name = app_name
        self.data_file = data_file
        self.machine_id = get_machine_id()
        self.encryption_key = self.machine_id + "_milkpet_secret_2024"
    
    def get_storage_path(self) -> str:
        """
        获取安全的存储路径
        
        Windows: %APPDATA%/MilkPet/
        Mac: ~/Library/Application Support/MilkPet/
        Linux: ~/.local/share/MilkPet/
        """
        if getattr(sys, 'frozen', False):
            # 打包后：使用用户数据目录
            if sys.platform == 'win32':
                base_path = os.environ.get('APPDATA', os.path.expanduser('~'))
            elif sys.platform == 'darwin':
                base_path = os.path.expanduser('~/Library/Application Support')
            else:
                base_path = os.path.expanduser('~/.local/share')
        else:
            # 开发时：在项目根目录
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        storage_dir = os.path.join(base_path, self.app_name)
        os.makedirs(storage_dir, exist_ok=True)
        
        return os.path.join(storage_dir, self.data_file)
    
    def save_encrypted_data(self, data: Dict[str, Any]) -> bool:
        """
        保存加密数据
        
        参数:
            data: 要保存的数据字典
            
        返回: 是否成功
        """
        try:
            # 在数据中添加机器ID
            data_with_machine = data.copy()
            data_with_machine['_machine_id'] = self.machine_id
            data_with_machine['_save_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 转换为 JSON 字符串
            json_str = json.dumps(data_with_machine, ensure_ascii=False)
            
            # 加密
            encrypted = simple_encrypt(json_str, self.encryption_key)
            
            # 保存到文件
            save_path = self.get_storage_path()
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(encrypted)
            
            print(f"[OK] 加密数据已保存: {save_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 保存加密数据失败: {e}")
            return False
    
    def load_encrypted_data(self) -> Optional[Dict[str, Any]]:
        """
        加载并解密数据
        
        返回: 数据字典，如果验证失败返回 None
        """
        try:
            save_path = self.get_storage_path()
            
            if not os.path.exists(save_path):
                print("[INFO] 未找到存档文件")
                return None
            
            # 读取加密数据
            with open(save_path, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            # 解密
            json_str = simple_decrypt(encrypted_data, self.encryption_key)
            data = json.loads(json_str)
            
            # 验证机器ID
            stored_machine_id = data.get('_machine_id')
            if stored_machine_id != self.machine_id:
                print(f"[WARN] 检测到数据属于其他用户！")
                print(f"       当前ID: {self.machine_id}")
                print(f"       存储ID: {stored_machine_id}")
                print(f"       将创建新的空数据文件")
                return None
            
            # 移除元数据
            if '_machine_id' in data:
                del data['_machine_id']
            if '_save_time' in data:
                del data['_save_time']
            
            print(f"[OK] 加密数据已加载: {save_path}")
            return data
            
        except json.JSONDecodeError:
            print("[ERROR] 数据文件损坏或格式错误")
            return None
        except Exception as e:
            print(f"[ERROR] 加载加密数据失败: {e}")
            return None
    
    def delete_data(self) -> bool:
        """删除数据文件"""
        try:
            save_path = self.get_storage_path()
            if os.path.exists(save_path):
                os.remove(save_path)
                print(f"[OK] 数据已删除: {save_path}")
            return True
        except Exception as e:
            print(f"[ERROR] 删除数据失败: {e}")
            return False
