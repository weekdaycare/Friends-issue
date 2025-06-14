# Friends-issue

[@xaoxuu](https://github.com/xaoxuu) 友链仓库的部分拓展版，部分改动如下：

- 友链数据 `data.json` 与友链文章 `posts.json` 分开存放（无法使用stellar新版友链UI）
- 增加邮件订阅功能
- 邮件推送本站点更新文章至订阅邮箱

---
## 配置

Fork我的仓库后，你只需要配置 `.github/workflows/` 下的几个工作流即可。

### Data Migration

数据迁移工作流，若你想从之前的友链仓库升级为此版本，只需要运行一次即可

### Issue Json Checker

抓取每个 issue 中第一个 json 数据块，合并为一个 `data.json` 文件。主要配置项如下

```yml
# 检查完毕后重新生成一下JSON
- name: Generate data.json
	uses: xaoxuu/issues2json@main
	with:
		data_version: 'v2'
		data_path: '/v2/data.json'
		sort: 'created-desc' # 'created-desc'/'created-asc'/'updated-desc'/'updated-asc'
		exclude_issue_with_labels: '审核中, 无法访问, 缺少互动, 缺少文章, 风险网站' # 具有哪些标签的issue不生成到JSON中
		hide_labels: 'subscribe' # 这些标签不显示在前端页面
```

- `data_version` 为生成数据中 version 字段的内容，保持默认即可。
- `data_path` 为生成的 json 数据存放路径。
- `sort` 为 json 数据的排序方式。
- `exclude_issue_with_labels` 为排除的 label，带有这些 label 的 issue 不会添加到最终 json 文件中。
- `hide_labels` 为前端移除标签，带有这些 label 的 issue 会添加到最终的 json，但是不会带有 label 数据。 

json 数据格式如下

```json
{
  "version": "v2",
  "content": [
    {
      "title": "",
      "url": "",
      "description": "",
      "icon": "",
      "snapshot": "",
      "feed": "",
      "issue_number": ,
      "labels": []
    }
  ]
}
```

### Issue Email Checker

检查 issue 中是否包含邮箱信息，如果包含，则为该 issue 打上 `subscribe` 标签，并输出总订阅邮箱 `subscribe.json`

```yml
- uses: weekdaycare/Issue-email-checker@main
	with:
		issue_state: open # closed
	env:
		GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- `issue_state` 默认检测状态为 `open` 的 issue。

json 数据格式如下

```json
{
  "emails": [
    "xiabee@duck.com"
  ]
}
```

### Email Pusher

定时抓取本站的 rss 数据，存放于 `last_articles.json` 中。当存在新文章时，将发邮件告知 `subscribe.json` 中的邮箱。

```yml
- name: Send Blog Update Email
	uses: weekdaycare/email-pusher@main
	with:
		rss_url: "https://weekdaycare.cn/atom.xml"
		smtp_server: "smtp.feishu.cn"
		smtp_port: 587
		sender_email: "comment@weekdaycare.cn"
		smtp_use_tls: "true"
		# email_template_url: ""
		subscribe_json_url: "https://raw.githubusercontent.com/weekdaycare/Friends-issue/output/v2/subscribe.json"
		website_title: "星日语"
		website_icon: "https://weekdaycare.cn/asset/avatar.svg"
		smtp_password: ${{ secrets.SMTP_PASSWORD }}
```

- `rss_url` 本站 rss 链接 
- `smtp_server` smtp 服务器地址
- `smtp_port` smtp 端口
- `sender_email` smtp 账号
- `smtp_password` smtp 密码，请在 secrets 中新建 `SMTP_PASSWORD` 并填入密码。
- `smtp_use_tls` smtp 是否使用 tls
- `email_template_url` 邮件模板链接
- `subscribe_json_url` subscribe 链接
- `website_title` 站点名称
- `website_icon` 站点图标

json 数据格式

```json
{
    "articles": [
        {
            "title": "",
            "link": "",
            "published": "",
            "summary": ""
        },
    ],
    "fail_count": 0
}
```

`fail_count` 为防错机制，避免偶然导致的空数据覆盖。

### Feed Posts Parser

抓取友链 rss 链接并解析文章生成 `posts.json` 数据。

```yml
- name: Run Feed Post Parser
	uses: weekdaycare/feed-posts-parser@main
	env:
		GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
	with:
		data_path: '/v2/posts.json'
		posts_count: 3
		date_format: 'YYYY-MM-DD HH:mm'
```

- `data_path` 文件路径
- `posts_count` 每个 rss 链接抓取文章数量
- `date_format` 生成数据中的日期格式

生成数据格式与 `hexo-circle-of-friends` 数据格式一致。

---
## 引用

基于github issue托管的友链管理工具。本项目已重构

本项目引用其他项目如下：

- [xaoxuu/issues2json](https://github.com/xaoxuu/issues2json)
- [xaoxuu/links-checker](https://github.com/xaoxuu/links-checker)
- [weekdaycare/feed-posts-parser](https://github.com/weekdaycare/feed-posts-parser)
- [weekdaycare/Issue-email-checker](https://github.com/weekdaycare/Issue-email-checker)
- [weekdaycare/email-pusher](https://github.com/weekdaycare/email-pusher)

---
## Todo List

- [x] 抓取友链文章并降序输出为 `json` 文件
- [x] 对订阅邮箱进行文章更新推送
- [ ] 友链文章更新日/周/月报