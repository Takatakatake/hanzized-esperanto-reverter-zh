import streamlit as st
import pandas as pd
import io
import re

# 页面设置
st.set_page_config(
    page_title="汉字化世界语 → 字母转换器",
    page_icon="🔤",
    layout="wide"
)

def load_default_csv():
    """加载默认CSV文件"""
    default_csv_path = "./エスペラント語根-漢字対応表_スニペット用最小限.csv"
    try:
        df = pd.read_csv(default_csv_path, header=None, names=['esperanto', 'kanji'])
        return df
    except Exception as e:
        st.error(f"加载默认CSV文件失败：{e}")
        return None

def create_kanji_to_esperanto_dict(df):
    """创建汉字→世界语词根的字典"""
    kanji_dict = {}
    max_length = 0
    
    for _, row in df.iterrows():
        esperanto = str(row['esperanto']).strip()
        kanji = str(row['kanji']).strip()
        
        # 跳过空值或nan
        if pd.isna(kanji) or kanji == '' or kanji == 'nan':
            continue
            
        # 将汉字及其后的特殊字符一起作为键
        kanji_dict[kanji] = esperanto
        max_length = max(max_length, len(kanji))
    
    return kanji_dict, max_length

def convert_kanji_esperanto_to_alphabet(text, kanji_dict, max_length):
    """将汉字化世界语转换为字母世界语"""
    result = []
    i = 0
    
    while i < len(text):
        # 保留空白字符
        if text[i].isspace():
            result.append(text[i])
            i += 1
            continue
        
        # 保留ASCII字符（字母、数字、符号）
        if ord(text[i]) < 128 or text[i] in '.,!?;:\'"()[]{}+-*/<>=':
            result.append(text[i])
            i += 1
            continue
        
        # 保留世界语特殊字符（ĉ, ĝ, ĥ, ĵ, ŝ, ŭ等）
        if text[i] in 'ĉĈĝĜĥĤĵĴŝŜŭŬ':
            result.append(text[i])
            i += 1
            continue
        
        # 查找汉字及其后的特殊字符（最长匹配）
        found = False
        # 检查到字典中最长条目的长度（从长到短）
        for length in range(min(max_length, len(text) - i), 0, -1):
            substring = text[i:i+length]
            if substring in kanji_dict:
                result.append(kanji_dict[substring])
                i += length
                found = True
                break
        
        if not found:
            # 如果在字典中未找到，则保持原样
            result.append(text[i])
            i += 1
    
    # 全部转换为小写
    converted_text = ''.join(result).lower()
    return converted_text

# 标题
st.title("🔤 汉字化世界语 → 字母转换器")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("📋 CSV文件设置")
    
    use_custom_csv = st.checkbox("使用自定义CSV文件", value=False)
    
    if use_custom_csv:
        uploaded_file = st.file_uploader(
            "上传世界语词根-汉字对照表",
            type=['csv'],
            help="CSV格式：世界语词根,汉字"
        )
    else:
        uploaded_file = None
        st.info("使用默认CSV文件")
    
    st.markdown("---")
    st.markdown("### 📖 使用方法")
    st.markdown("""
    1. **CSV文件**：选择默认或自定义CSV
    2. **输入**：输入汉字化世界语文本
    3. **转换**：点击转换按钮
    4. **结果**：显示字母世界语文本
    """)

# 主要内容
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 输入（汉字化世界语）")
    
    # 默认示例文本
    default_text = """我 听is, ke 间 反更 比 周o 和 从 二 多样aj 人ʜoj 内 反同aj 处ʟoj, ke kumino 很 好e 适as 为 la 羊物a 大盘o "jingisukan".
我 实际e 试is kuminon 共 jingisukan, 和 我 全e 同意as: kumino 真e 好e 协议as kun la 羊物a 大盘o.
从 今, 何时 我 吃os jingisukan, 我 决is 全时 辛i la 肉ᴠon 以 kumino."""
    
    input_text = st.text_area(
        "请输入汉字化世界语文本",
        value=default_text,
        height=300,
        help="可以输入混有汉字和字母的文本"
    )

with col2:
    st.subheader("✅ 输出（字母世界语）")
    
    # 加载CSV文件
    if use_custom_csv and uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, header=None, names=['esperanto', 'kanji'])
            st.success("✓ 已加载自定义CSV文件")
        except Exception as e:
            st.error(f"CSV文件加载失败：{e}")
            df = None
    else:
        df = load_default_csv()
        if df is not None:
            st.success("✓ 已加载默认CSV文件")
    
    # 转换处理
    if df is not None and st.button("🔄 转换", type="primary", use_container_width=True):
        with st.spinner("转换中..."):
            kanji_dict, max_length = create_kanji_to_esperanto_dict(df)
            
            if kanji_dict:
                converted_text = convert_kanji_esperanto_to_alphabet(input_text, kanji_dict, max_length)
                
                st.text_area(
                    "转换结果",
                    value=converted_text,
                    height=300,
                    help="全部小写的世界语文本"
                )
                
                # 下载按钮
                st.download_button(
                    label="📥 下载文本",
                    data=converted_text,
                    file_name="converted_esperanto.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
                # 统计信息
                st.markdown("---")
                st.markdown("### 📊 统计")
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                with col_stat1:
                    st.metric("输入字符数", len(input_text))
                with col_stat2:
                    st.metric("输出字符数", len(converted_text))
                with col_stat3:
                    st.metric("字典条目数", len(kanji_dict))
                with col_stat4:
                    st.metric("最长条目", f"{max_length}字符")
            else:
                st.error("字典创建失败")
    else:
        st.info("👆 请点击转换按钮")

# 页脚
st.markdown("---")
with st.expander("ℹ️ 关于本应用"):
    st.markdown("""
    ### 汉字化世界语 → 字母转换应用
    
    本应用是一个将用汉字表示的世界语词根还原为原始字母表示的工具。
    
    **特点：**
    - 可使用默认对照表，也可上传自定义CSV文件
    - 支持汉字和字母混合的文本
    - 正确处理特殊字符（ʜ, ɪ, ʟ, ᴠ等）
    - 转换结果全部输出为小写
    
    **CSV文件格式：**
    ```
    世界语词根,汉字
    mi,我
    aŭd,听
    kun,共
    ```
    
    **关于世界语：**
    世界语（Esperanto）是一种人工语言，旨在成为国际辅助语言。
    本工具可以帮助您将汉字化的世界语文本转换回标准的字母形式。
    """)
