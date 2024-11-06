# Friends-issue

基于github issue托管的友链管理工具，整合 [issues-json-generator](https://github.com/xaoxuu/issues-json-generator) 与 [Friend-Circle-Lite](https://github.com/willow-god/Friend-Circle-Lite) 的功能，一个仓库完成友链管理，朋友圈构建与邮箱订阅等功能。

简单来说它将自动提取本仓库 issues 中第一段 `JSON` 代码块并保存到仓库中，同时会提取 `subscribe` 标签下所有 open 状态的 issue 中的 `email` 地址，生成静态 json 数据，你可以根据

例如动态友链：https://github.com/xaoxuu/friends

随意发挥你的创意吧～

## 使用方法

1. fork 本仓库，把 `config.yml` 配置改为自己的：

```yaml
issues:
  repo: weekdaycare/Friends-issue # 仓库持有者/仓库名
  label: active  # 只能配置1个或留空，留空则所有open的issue都会被抓取。配置1个时，issue只有在具有该标签时才被抓取
  groups: # 填写用来分组的label名称。留空则所有被抓取的issue输出至data.json，否则按照输出与组名同名的json文件
  sort: updated-desc # 排序，按最近更新，取消此项则按创建时间排序
```
配置实例说明如下
| label         | groups                      | 输出文件                | 抓取issue                                         |
| ------------- | --------------------------- | ----------------------- | ------------------------------------------------- |
| label: active | groups:                     | data.json               | 所有open的、label包含active的issue                |
| label: active | groups: ["ordinary", "top"] | ordinary.json, top.json | open的、label包含active且包含ordinary或top的issue |
| label:        | groups:                     | data.json               | 所有open的issue                                   |
| label:        | groups: ["ordinary", "top"] | ordinary.json, top.json | open的、label包含ordinary或top的issue             |

2. 打开 action 运行权限。

其他配置可见 [Friend-Circle-Lite](https://github.com/willow-god/Friend-Circle-Lite) 文档

与 Friend-Circle-Lite 邮件订阅的格式不同，我将邮件订阅功能集成在 issue 申请中，你可以在申请友链时填写邮箱获取订阅功能，也可以仅订阅本站不交换友链。action 会自动检测你的 issue 中是否包含 email 地址。如果想要取消订阅，关闭 issue 或者将邮箱地址置空即可。

## 测试是否配置成功

1. 新建 issue 并按照模板要求填写提交。
2. 当你的 issue 中包含邮箱地址时 action 会自动为该 issue 打上 `subscribe` 标签
3. 等待 Action 运行完毕，检查 `output` 分支是否有 `/v2/data.json` 文件或`/v2/<组名>.json`，内容是否正确，如果正确则表示已经配置成功。


## IJGP 协议

> 本项目基于 **[IJGP v1](https://github.com/topics/ijgp)** 协议，全称为 **Issues-Json Generator Protocol**

## output 输出

| 字段 | 类型 | 用途 |
| :-- | :-- | :-- |
| title | string | 主标题 |
| url | string | 主链接 |
| avatar | string | 头像链接 |
| description | string | 描述，建议200字以内 |
| keywords | string | 关键词，英文逗号隔开 |
| screenshot | string | 屏幕截图 |

### 友链 json 输出格式

```json data.json
{
  "content": [
    {
      "title": "",
      "url": "",
      "avatar": "",
      ...
    }
    ...
  ]
}
```

### email 订阅输出格式

朋友圈数据

```json all.json
{
  "statistical_data": {
    "friends_num": num,
    "active_num": num,
    "error_num": num,
    "article_num": num,
    "last_updated_time": ""
  },
  "article_data": [
    {
      "title": "",
      "created": "",
      "link": "",
      "author": "",
      "avatar": ""
    },
    ...
  ]
}
```

## page 输出

包含静态页面与文件，你可以将其部署在 github page 或者 vercel cloudflare 等其他地方，具体使用请参考 Friend-Circle-Lite 官方文档。