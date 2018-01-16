# GSIL(GitHub Sensitive Information Leak)
> Monitor Github sensitive information leaks in near real time and send alert notifications.

> 近实时监控Github敏感信息泄露，并发送告警通知。

## Installation(安装)
```
git clone https://github.com/FeeiCN/gsil.git
cd gsil/
pip install -r requirements.txt
```

## Configuration(配置)
#### gsil/config.gsil: 告警邮箱和Github配置
```
[mail]
host : smtp.exmail.qq.com
port : 25
mails : gsil@domain.com
from : GSIL
password : your_password
to : feei@feei.cn

[github]
# 扫描到的是否立刻Clone到本地
clone: false

# Github Token用来调用相关API
# https://github.com/settings/tokens
tokens : 81395d57fab0550c426c216ca717746d2ce1d7e7,4f29ddc5f0d8fa0841a2fdc557cf9941e28d5123,f0f41b08f6146b3fd7e4c74e35b8eddd9d87b76f,ed0e0c8f5afb170c475c8fb8703e0972b10c3a21,2378badc29e41939863978ef886fd9cf01c91bc0,bdbe6402f605805b304bc03324f2e0423bbe4efd,070d7c44cb97af94fbf872b5419bebe6726d1b37,8414b778c60aca40d83aeee9c6bcd6e4d91cf284,f908391378fbc047bcf432d1d16e8c9f8681cd59,600f1fa50aae4ea65dade960a823e3a642da89ce,f1765571eb36aaa7ec49fb964285a6f5918478fe,edd4096cb3b13a40c8d1414cf809cd26f9d2305f,d49141037bacd411e1f99b8949b558509e0e4572,b8a408437b156f93d9db4f6b2044d618b5daefaf,efcfdaa8c361b54f04e3bd060bcbfa7bda89f721,8755d755a4a6f710a0dbb9839106144d35d00f6c

```
#### gsil/rules.gsil: 扫描规则
> 规则一般选用内网独立的特征，比如蘑菇街的外网是mogujie.com，蘑菇街的内网是mogujie.org，则可以将mogujie.org作为一条规则。
> 其它还有类似代码头部特征、外部邮箱特征等

| 字段 | 意义 | 选填 | 默认 | 描述 |
| --- | --- | --- | --- | --- |
| keyword | 关键词 | 必填 | - | 多个关键词可以用空格，比如‘账号 密码’；某些关键字出现的结果非常多，所以需要精确搜索时可以用双引号括起来，比如‘”ele.me“’；|
| ext | 指定文件后缀 | 可选 | 全部后缀 | 多个后缀可以使用英文半角逗号（,）分隔，比如`java,php,python` |
| mode |  匹配模式 | 可选 | 正常匹配 | 正常匹配：匹配包含keyword的行，并记录该行附近行 / 仅匹配：仅匹配包含keyword行 / 全部匹配（不推荐使用）：搜出来的整个问题都算作结果 |

```
{
    # 一级分类，一般使用公司名，用作开启扫描的第一个参数（python gsil.py test）
    "test": {
        # 二级分类，一般使用产品线
        "mogujie.com": {
            # 公司内部域名
            "\"mogujie.org\"": {},
            # 公司代码特征
            "copyright meili inc": {},
            # 内部主机域名
            "yewu1.db.mogujie.host": {},
            # 外部邮箱
            "mail.mogujie.com": {}
        }
    }
}
```


## Usage(用法)

```
python gsil.py test
```

```bash
$ crontab -e

# 每个小时运行一次
0 * * * * /usr/bin/python /var/app/gsil/gsil.py test > /tmp/gsil
# 每天晚上11点发送统计报告
0 23 * * * /usr/bin/python /var/app/gsil/gsil.py --report
```
