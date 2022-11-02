### 改进项目 ###
1. 使用 `actions/cache@v2` 替代 `commit` 保存新的 `REFRESH_TOKEN`
1. 同时将新的`REFRESH_TOKEN` 保存到 `artifact`

### 获得 refresh_token ###
https://rclone.org/downloads/

./rclone authorize "onedrive" "应用程序(客户端)ID" "应用程序密码"

复制 refresh_token 值

### 设置方式 ###
依次点击上栏Setting > Secrets > Add a new secret，新建 secret：

  内容分别如下: ( 把你的应用id改成你的应用id , 你的应用机密改成你的机密，单引号不要动 )
  
  - CLIENT_ID：`你的应用id`
  - CLIENT_SECRET：`你的应用机密`
  - REFRESH_TOKEN：`你的REFRESH_TOKEN`
  
### 更新`REFRESH_TOKEN` ###
  前往 Actions - Caches 页面，找到 refresh_token 删除。
  前往 Settings - Secrets - Actions 页面，编辑 REFRESH_TOKEN 并填入新值。


  
### Thanks ###
* https://github.com/wangziyingwen/AutoApiSecret
