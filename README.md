# Friends-issue

基于github issue托管的友链管理工具，整合 [issues-json-generator](https://github.com/xaoxuu/issues-json-generator) 与 [Friend-Circle-Lite](https://github.com/willow-god/Friend-Circle-Lite) 的功能，一个仓库完成友链管理，朋友圈构建与邮箱订阅等功能。

简单来说它将自动提取本仓库 issues 中第一段 `JSON` 代码块并保存到仓库中，同时会提取 `subscribe` 标签下所有 open 状态的 issue 中的 `email` 地址，生成静态 json 数据，你可以根据 json 数据撰写前端页面，例如动态友链：https://weekdaycare.cn/about

## 使用方法

1. fork 本仓库，把 `config.yaml` 配置改为自己的：

### 友链配置

```yaml
# 友链设置
# 网络请求设置
request:
  timeout: 10 # 超时设置
  ssl: true # ssl设置

# 要抓取的 issues 配置
issues:
  repo: # weekdaycare/Friends-issue 仓库持有者/仓库名
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


### 朋友圈配置

基本配置与 [Friend-Circle-Lite](https://github.com/willow-god/Friend-Circle-Lite) 保持相同

```yaml
# 爬虫相关配置
# 解释：使用request实现友链文章爬取，并放置到根目录的all.json下
#   enable:             是否启用爬虫
#   json_url:           请填写对应格式json的地址或github repo，不填默认为本仓库 issue
#   article_count:      请填写每个博客需要获取的最大文章数量
#   expire_date:        请填写文章过期时间，过滤超时文章
#   marge_result:       是否合并多个json文件，若为true则会合并指定网络地址和本地地址的json文件
#     enable:           是否启用合并功能，该功能提供与自部署的友链合并功能，可以解决服务器部分国外网站无法访问的问题
#     marge_json_path:  请填写网络地址的json文件，用于合并，不带空格！！！
spider_settings:
  enable: true
  json_url: # "weekdaycare/Friends-issue" 不填默认本仓库，也可以填写远程url
  article_count: 5
  expire_date: 60
  merge_result:
    enable: false
    merge_json_url: ""

# 邮箱推送功能配置，暂未实现，等待后续开发
# 解释：每天为指定邮箱推送所有友链文章的更新，仅能指定一个
#   enable:             是否启用邮箱推送功能
#   to_email:           收件人邮箱地址
#   subject:            邮件主题
#   body_template:      邮件正文的 HTML 模板文件
email_push:
  enable: false
  to_email: recipient@example.com
  subject: "今天的 RSS 订阅更新"
  body_template: "rss_template.html"

# 邮箱issue订阅功能配置
# 解释：向在issue中提取的所有邮箱推送您网站中的更新，添加邮箱和删除邮箱均通过添加issue对应格式实现
#   enable:             是否启用邮箱推送功能
#   your_blog_url:      你的博客地址
#   website_info:       你的博客信息
#     title:            你的博客标题，如果启用了推送，用于生成邮件主题
rss_subscribe:
  enable: true
  your_blog_url: https://weekdaycare.cn/
  email_template: "./rss_subscribe/email_template.html"
  website_info:
    title: "星日语"

# SMTP 配置
# 解释：使用其中的相关配置实现上面两种功能，若无推送要求可以不配置，请将以上两个配置置为false
#   email:              发件人邮箱地址
#   server：            SMTP 服务器地址
#   port：              SMTP 端口号
#   use_tls：           是否使用 tls 加密
smtp:
  email: comment@weekdaycare.cn
  server: smtp.feishu.cn
  port: 587
  use_tls: true

# 特殊RSS地址指定，可以置空但是不要删除！
# 解释：用于指定特殊RSS地址，如B站专栏等不常见RSS地址后缀，可以添加多个
#   name:               友链名称
#   url:                指定的RSS地址
specific_RSS:
  # - name: "Redish101"
  #   url: "https://reblog.redish101.top/api/feed"
  # - name: "無名小栈"
  #   url: "https://blog.imsyy.top/rss.xml"
```

2. 创建 5 个 issue 标签，分别是
    
   - `active`     友链添加成功
   - `checklist`  部分条件未满足
   - `suspend`    请及时添加本站友链
   - `404`        您的网站打不开
   - `subscribe`  欢迎订阅本博客
  
当然，如果你需要配置友链分组，你可以加上其他的标签，并在 `config.yaml` 中配置 `groups` 分组

3. 打开 action 运行权限。

其他配置可见 [Friend-Circle-Lite](https://github.com/willow-god/Friend-Circle-Lite) 文档

与 Friend-Circle-Lite 邮件订阅的格式不同，我将邮件订阅功能集成在 issue 申请中，你可以在申请友链时填写邮箱获取订阅功能，也可以仅订阅本站不交换友链。action 会自动检测你的 issue 中是否包含 email 地址。如果想要取消订阅，关闭 issue 或者将邮箱地址置空即可。

## 测试是否配置成功

1. 新建 issue 并按照模板要求填写提交。
2. 当你的 issue 中包含邮箱地址时 action 会自动为该 issue 打上 `subscribe` 标签
3. 等待 Action 运行完毕，检查 `output` 分支是否有 `/v2/data.json` 文件或 `/v2/<组名>.json`， `page` 分支内容是否正确，如果正确则表示已经配置成功。

## output 分支

output 分支中包含两部分数据

1. 友链信息 `data.json` 或 `<分组名>.json`

```json
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

| 字段 | 类型 | 用途 |
| :-- | :-- | :-- |
| title | string | 主标题 |
| url | string | 主链接 |
| avatar | string | 头像链接 |
| description | string | 描述，建议200字以内 |
| keywords | string | 关键词，英文逗号隔开 |
| screenshot | string | 屏幕截图 |

2. 邮箱订阅信息 subscribe.json

请注意，填写邮箱地址意味着你的邮箱对其他人也是公开的。

```json
{
  "emails": [
    "xxx@email.com",
    ...
  ]
}
```

## page 分支

包含静态页面与文件，你可以将其部署在 github page 或者 vercel cloudflare 等其他地方，具体使用请参考 Friend-Circle-Lite 官方文档。

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

## 从其他项目迁移

若你正在使用 [issues-json-generator](https://github.com/xaoxuu/issues-json-generator) ，你可以将 issue 迁移至你 fork 的仓库中。或者你可以更改配置使本仓库能够抓取你的 issue ，但是邮箱订阅需要在本仓库提 issue 申请。

## IJGP 协议

> 本项目基于 **[IJGP v1](https://github.com/topics/ijgp)** 协议，全称为 **Issues-Json Generator Protocol**