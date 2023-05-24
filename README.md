# Bianace 分析

通过对接 Bianace 进行财务分析

## 获取 API key

获取流程：

1. 登录币安账户，点击【用户中心】-【API管理】，进入API管理页面。
2. 设置一个API密钥（即API名称），点击【创建 API】。
3. 点击【获取验证码】，输入邮箱验证码、手机验证码和谷歌验证码，然后点击【提交】。

## 快速启动

1. 依赖安装

   ```shell
   cd MyBinance
   
   pip install -r requirements.txt
   ```

2. 编辑工程根目录中的 `config.ini`。
   + 配置 Bianace API key

3. 启动 `streamlit`

   ```shell
   streamlit run main.py
   ```

