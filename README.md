# 三要素实名核验 API 快速开始（Python）

10 分钟跑通三要素核验：姓名 + 身份证号 + 本人照片（人脸比对）。只用 Python 标准库，无需安装依赖。

> 鉴权只有一个请求头 `X-API-Key`，JSON 进、JSON 出，不需要签名。
> **示例用假数据，请填入自己的密钥和测试数据。**

## 30 秒跑起来

```bash
git clone https://github.com/liuq88450-del/realname-api-quickstart.git
cd realname-api-quickstart

# 演示模式：不发真实请求，验证代码结构
python3 realname_quickstart.py --demo
```

## 真实接入（4 步）

### 1. 领免费试用

提交试用申请后发 Key：三要素 **100 次**，7 天有效。

### 2. 填配置

```bash
export RN_BASE_URL="https://<开通时给的域名>"
export RN_API_KEY="ak_live_xxx"
```

Windows PowerShell：

```powershell
$env:RN_BASE_URL="https://<开通时给的域名>"
$env:RN_API_KEY="ak_live_xxx"
```

### 3. 发一笔请求

```bash
python3 realname_quickstart.py \
  --name "张三" --idcard "110101199001011234" --photo ./my-photo.jpg
```

### 4. 看返回

```json
{
  "code": "OK",
  "request_id": "r_...",
  "result": { "match": true, "level": "realname" },
  "billed": true
}
```

返回码：`OK` 一致、`NO_MATCH` 不一致（人脸不像 / 身份信息不匹配，都算核验完成、计费）、`IMAGE_INVALID` 照片不合格（不计费）、`PARAM_INVALID` 参数错、`KEY_INVALID` Key 无效、`RATE_LIMITED` 超 QPS、`QUOTA_EXCEEDED` 余额不足、`UPSTREAM_TIMEOUT` / `UPSTREAM_ERROR` 上游异常。

## 示例数据说明

示例里的姓名、证件号是**虚构占位**；照片必须用你自己的测试图（**JPG，5–50KB**，脚本会自动转 Base64 并去掉 `data:` 前缀）。照片不合格返回 `IMAGE_INVALID`，不计费。

## 生产环境还要做

- Key 只放服务端，用环境变量注入；
- 日志记录 `request_id`，证件号打码，**不留存照片**；
- 用 `Idempotency-Key` 做幂等，重试不重复计费；
- 超时、退避、余额告警。

## 文件

```
realname-api-quickstart/
├── realname_quickstart.py   # 单文件示例，演示 + 真实两种模式
├── README.md
├── LICENSE
└── .gitignore
```

## 许可

MIT。

---

*维护：小通｜更新：2026-11-10*
