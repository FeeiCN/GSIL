# GSIL(GitHub敏感信息泄露)

[English documents](https://github.com/FeeiCN/GSIL/blob/master/README.md)

> 近实时监控GitHub敏感信息泄露，并发送告警通知。

## 安装

> 仅在Python3下验证过

```bash
$ git clone https://github.com/FeeiCN/GSIL.git
$ cd GSIL/
$ pip install -r requirements.txt
```

## 配置

### gsil/config.gsil.cfg(复制config.gsil.cfg.example并重命名): 告警邮箱和Github配置

```
[mail]
host : smtp.exmail.qq.com
# SMTP端口(非SSL端口，但会使用TLS加密)
port : 25
# 多个发件人使用逗号(,)分隔
mails : gsil@feei.cn
from : GSIL
password : your_password
# 多个收件人使用逗号(,)分隔
to : feei@feei.cn

[github]
# 扫描到的漏洞仓库是否立刻Clone到本地（~/.gsil/codes/）
# 此选项用作监控其它厂商，避免因为仓库所有者发现后被删除
clone: false

# GitHub Token用来调用相关API，多个Token使用逗号(,)分隔
# https://github.com/settings/tokens
tokens : your_token
```

### gsil/rules.gsil.yaml(复制rules.gsil.yaml.example并重命名): 扫描规则

> 规则一般选用内网独立的特征，比如蘑菇街的外网是mogujie.com，蘑菇街的内网是mogujie.org，则可以将mogujie.org作为一条规则。

> 其它还有类似代码头部特征、外部邮箱特征等

| 字段 | 意义 | 选填 | 默认 | 描述 |
| --- | --- | --- | --- | --- |
| keyword | 关键词 | 必填 | - | 多个关键词可以用空格，比如‘账号 密码’；某些关键字出现的结果非常多，所以需要精确搜索时可以用双引号括起来，比如‘”ele.me“’；|
| ext | 指定文件后缀 | 可选 | 全部后缀 | 多个后缀可以使用英文半角逗号（,）分隔，比如`java,php,python` |
| mode |  匹配模式 | 可选 | 正常匹配(normal-match) | 正常匹配(normal-match)：匹配包含keyword的行，并记录该行附近行 / 仅匹配(only-match)：仅匹配包含keyword行 / 全部匹配(full-match)（不推荐使用）：搜出来的整个问题都算作结果 |

```
{
    # 一级分类，一般使用公司名，用作开启扫描的第一个参数（python gsil.py test）
    "test": {
        # 二级分类，一般使用产品线
        "mogujie": {
            # 公司内部域名
            "\"mogujie.org\"": {
                # mode/ext默认可不填
                "mode": "normal-match",
                "ext": "php,java,python,go,js,properties"
            },
            # 公司代码特征
            "copyright meili inc": {},
            # 内部主机域名
            "yewu1.db.mogujie.host": {},
            # 外部邮箱
            "mail.mogujie.com": {}
        },
        "meilishuo": {
            "meilishuo.org": {},
            "meilishuo.io": {}
        }
    }
}
```

## 用法

```bash
# 启动测试
$ python gsil.py test

# 测试token有效性
$ python gsil.py --verify-tokens
```
**GSIL 由原来的 crontab 启动改为了常驻进程，有多少个 token 将启动多少个子进程，建议使用 supervisor 去管理而不是使用命令行。**

如果你只是测试，可以使用如下命令：
```bash
$ python gsil.py test
```
* 扫描报告过一次的将不会重复报告，缓存记录在~/.gsil/目录

* ~/.gsil/目录增加json格式的扫描结果，可使用 Kafka 等进行消费

## 引用
- [GSIL详细介绍](http://feei.cn/gsil)
