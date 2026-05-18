# -*- coding: utf-8 -*-
"""
诊断脚本 - 直接读取存储文件内容
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnose_storage():
    """诊断存储文件的实际内容"""
    print("=" * 70)
    print("🔬 存储文件诊断工具")
    print("=" * 70)
    
    try:
        from basic_model.secure_storage import SecureStorage, simple_decrypt
        
        storage = SecureStorage()
        save_path = storage.get_storage_path()
        
        print(f"\n📁 文件路径: {save_path}")
        print(f"📂 是否存在: {os.path.exists(save_path)}")
        
        if not os.path.exists(save_path):
            print("\n❌ 文件不存在！")
            return
        
        file_size = os.path.getsize(save_path)
        print(f"📏 文件大小: {file_size} 字节")
        print(f"⏰ 修改时间: {os.path.getmtime(save_path)}")
        
        # 读取原始加密内容
        with open(save_path, 'r', encoding='utf-8') as f:
            encrypted_content = f.read()
        
        print(f"\n🔐 加密内容长度: {len(encrypted_content)} 字符")
        print(f"🔐 前200字符: {encrypted_content[:200]}...")
        print(f"🔐 后200字符: ...{encrypted_content[-200:]}")
        
        # 尝试解密
        print("\n🔓 尝试解密...")
        try:
            json_str = simple_decrypt(encrypted_content, storage.encryption_key)
            data = json.loads(json_str)
            
            print("\n✅ 解密成功！实际存储的数据:")
            print("-" * 70)
            
            # 显示所有键
            print(f"\n📋 数据键列表: {list(data.keys())}")
            
            # 显示 settings
            if 'settings' in data:
                settings = data['settings']
                print(f"\n⚙️  Settings:")
                print(f"   - pet_name: {settings.get('pet_name', '❌ 缺失')}")
                print(f"   - user_title: {settings.get('user_title', '❌ 缺失')}")
                print(f"   完整内容: {settings}")
            else:
                print("\n⚠️  没有 'settings' 键！")
            
            # 显示 custom_dialogs
            if 'custom_dialogs' in data:
                dialogs = data['custom_dialogs']
                print(f"\n💬 Custom Dialogs ({len(dialogs)} 条):")
                for i, dialog in enumerate(dialogs, 1):
                    print(f"   {i}. {dialog}")
            else:
                print("\n⚠️  没有 'custom_dialogs' 键！")
            
            # 显示 use_custom_only
            if 'use_custom_only' in data:
                print(f"\n☑️  Use Custom Only: {data['use_custom_only']}")
            else:
                print("\n⚠️  没有 'use_custom_only' 键！")
            
            # 显示元数据
            if '_machine_id' in data:
                print(f"\n🖥️  Machine ID (stored): {data['_machine_id']}")
                print(f"🖥️  Machine ID (current): {storage.machine_id}")
                print(f"   匹配: {'✅' if data['_machine_id'] == storage.machine_id else '❌ 不匹配!'}")
            
            if '_save_time' in data:
                print(f"⏰ Save Time: {data['_save_time']}")
            
            print("\n" + "=" * 70)
            print("🎯 诊断结论:")
            print("=" * 70)
            
            has_settings = 'settings' in data and len(data.get('settings', {})) > 0
            has_dialogs = 'custom_dialogs' in data and len(data.get('custom_dialogs', [])) > 0
            
            if has_settings and has_dialogs:
                print("✅ 文件中包含完整数据，问题可能在读取逻辑")
            elif not has_settings and not has_dialogs:
                print("❌ 文件中没有有效数据！保存可能失败或被清空")
            elif has_settings and not has_dialogs:
                print("⚠️  有设置但没有对话数据")
            elif not has_settings and has_dialogs:
                print("⚠️  有对话但没有设置数据")
                
        except Exception as decrypt_error:
            print(f"\n❌ 解密失败: {decrypt_error}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"\n❌ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    diagnose_storage()
    
    print("\n按回车键退出...")
    input()
