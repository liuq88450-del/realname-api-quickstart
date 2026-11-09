# 实名核验 API 快速开始（Python）

10 分钟跑通二要素 / 三要素核验的示例仓库。只用 Python 标准库，不需要装包。

> 接口域名、路径、字段名、签名规则以开通时下发的正式文档为准；本仓库里的写法是结构示意，填好配置即可替换。

## 30 秒跑起来

```bash
git clone https://github.com/liuq88450-del/realname-api-quickstart.git
cd realname-api-quickstart

# 演示模式：不发真实请求，验证代码结构
python3 realname_quickstart.py --demo
```

看到 `结论：一致（result=1）` 就说明代码能跑。

## 真实接入（4 步）

### 1. 领免费额度

注册后自动发放：二要素 100 条、三要素 50 条，各限 1 次，7 天有效。

### 2. 填配置

```bash
export RN_BASE_URL="https://<正式文档里的域名>"
export RN_APP_ID="app_xxxxx"
export RN_APP_SECRET="<开通邮件里的密钥>"
```

Windows PowerShell：

```powershell
$env:RN_BASE_URL="https://<正式文档里的域名>"
$env:RN_APP_ID="app_xxxxx"
$env:RN_APP_SECRET="<开通邮件里的密钥>"
```

### 3. 发一笔二要素

```bash
python3 realname_quickstart.py two \
  --name "张*" --idcard "110101********1234"
```

### 4. 发一笔三要素

```bash
python3 realname_quickstart.py three \
  --name "张*" --idcard "110101********1234" --mobile "138****5678"
```

> **示例用假数据，请填入自己的密钥。** 示例里的姓名、证件号、手机号、app_id 都是脱敏占位，换成自己的测试数据；不要用真实客户数据。

## 返回结构

```json
{
  "code": "0",
  "msg": "success",
  "request_id": "req_...",
  "order_no": "quickstart-...",
  "result": 1,
  "result_desc": "一致"
}
```

`result`：1 一致 / 2 不一致 / 3 查无记录（以正式文档为准）。

## 要改哪几个地方

| 位置 | 说明 |
|---|---|
| `PATH_TWO` / `PATH_THREE` | 接口路径，按正式文档替换 |
| `build_sign()` | 签名算法与拼接规则，按正式文档替换 |
| `build_payload()` | 字段名（如 `app_id`、`order_no`）按正式文档核对 |
| `RN_*` 环境变量 | 域名与密钥，不要写进代码 |

## 生产环境还要做

- 密钥放服务端 / 环境变量 / 配置中心，不进前端、不进仓库；
- 日志记录 `request_id`、`order_no`，并对证件号、手机号脱敏；
- 用 `order_no` 做幂等，重试不重复计费；
- 超时 3s/8s、指数退避重试、错误率熔断；
- 余额告警。

## 文件

```
realname-api-quickstart/
├── realname_quickstart.py   # 单文件示例，演示 + 真实两种模式
├── README.md
├── LICENSE
└── .gitignore
```

## 许可

MIT。示例代码可自由用于你的项目。

---

*维护：小通｜更新：2026-11-09*
