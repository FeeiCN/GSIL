# GSIL(GitHub Sensitive Information Leakage)

[中文文档](https://github.com/FeeiCN/GSIL/blob/master/README-zh.md)

> Monitor Github sensitive information leaks in near real time and send alert notifications.

## Installation

> Python3(Python2 is not tested)

```bash
$ git clone https://github.com/FeeiCN/gsil.git
$ cd gsil/
$ pip install -r requirements.txt
```

## Configuration

### gsil/config.gsil(Rename by config.gsil.example): Alarm mailbox and Github configuration

```conf
[mail]
host : smtp.exmail.qq.com
# SMTP port (Not SSL port, but will use TLS encryption)
port : 25
# Multiple senders are separated by comma (,)
mails : gsil@domain.com
from : GSIL
password : your_password
# Multiple recipients are separated by comma (,)
to : feei@feei.cn

[github]
# Whether the scanned data will be cloned to the local area immediately
# Clone to ~/.gsil/codes/ directory
clone: false

# Github Token, multiple tokens are separated by comma (,)
# https://github.com/settings/tokens
tokens : your_token
```

### gsil/rules.gsil(Rename by rules.gsil.example): scanning rules

> Generally, The best rule is the characteristic code of the intranet(Example: mogujie's extranet is `mogujie.com`, intranet is `mogujie.org`. At this time, `mogujie.org` can be used as a rule)

> There are other similar code head characteristic code, external mailbox characteristic code, and so on

| field | meaning | optional | default | describe |
| --- | --- | --- | --- | --- |
| keyword | key word | required | - | When multiple keywords are used, space segmentation is used(Example: `'username password'`), When you need a precise search, use double(Example: `"quotesele.me"`) |
| ext | file suffix | optional | all suffixes | Multiple suffixes are separated by comma(Example: `java,php,python`) |
| mode |  matching mode | optional | normal-match | `normal-match`(The line that contains the keyword is matched, and the line near the line is matched) / `only-match`(Only the lines that match the key words) / `full-match`(Not recommended for use)(The search results show the entire file)|

```
{
    # usually using the company name, used as the first parameter to open the scan(Example:`python gsil.py test`)
    "test": {
        # General use of product name
        "mogujie": {
            # Internal domain name of the company
            "\"mogujie.org\"": {
                # mode/ext options no need to configure by default
                "mode": "normal-match",
                "ext": "php,java,python,go,js,properties"
            },
            # Company code's characteristic code
            "copyright meili inc": {},
            # Internal host domain name
            "yewu1.db.mogujie.host": {},
            # External mailbox
            "mail.mogujie.com": {}
        },
        "meilishuo": {
            "meilishuo.org": {},
            "meilishuo.io": {}
        }
    }
}
```

## Usage

```bash
$ python gsil.py test

# Verify tokens validity
$ python gsil.py --verify-tokens
```

```bash
$ crontab -e

# Run every hour
0 * * * * /usr/bin/python /var/app/gsil/gsil.py test > /tmp/gsil
# Send a statistical report at 11 p. m. every night
0 23 * * * /usr/bin/python /var/app/gsil/gsil.py --report
```
* Once the scan report will not repeat the report, the cache records in ~/.gsil/ directory *

## Reference
- [GSIL详细介绍](http://feei.cn/gsil)
