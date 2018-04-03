<!-- TOC START min:1 max:3 link:true update:true -->
- [URI 格式规范](#uri-)
  - [URI格式定义](#uri)
    - [资源的原型](#)
    - [资源命名规范：](#-1)
  - [HTTP交互设计](#http)
    - [HTTP请求方法的使用](#http-1)
    - [响应状态码](#-2)
    - [元数据](#-3)
  - [授权与验证](#-4)
  - [限流rate limit](#rate-limit)
  - [Hypermedia API](#hypermedia-api)
  - [编写优秀的文档](#-5)
- [REST开发工具](#rest)
- [rest 和 soap](#rest--soap)

<!-- TOC END -->

# URI 格式规范
一个资源一般对应一个唯一的URI(URL)
## URI格式定义

``` URI = scheme "://" authority "/" path [ "?" query ] [ "#" fragment ]```
+ 分隔符 “/” 对URI 资源层级的划分
+ 使用连字符代替下划线： 超链接
+ 大小写敏感，统一使用小写
+ 不包含文件的扩展命，设置Http Header中的 Content-Tpye

### 资源的原型
+ 文档： 一个对象，或数据库中一条记录
+ 集合： 资源的容器（目录）
+ 仓库： 客户端管理的一个资源库
+ 控制器：执行一个方法，支持参数输入，返回结果。未来除增删改查（CRUD）以外的逻辑操作

### 资源命名规范：
+ 文档： 名词单数
+ 集合： 名词复数
+ 仓库： 名词复数
+ 控制器： 动词
+ 某些字段可以是遍历
例子:
模仿 github
root： https://api.github.com
GET /repos/:owner/:repo/git/commits/:sha
Response：
Get /leagues/teams/：teams/players/：name
Parameters：(name,type,description)
Optional Parameters
input example
Response
+ CRUD的操作不要体现在URI中

#### query字段
+ 过滤条件来使用.比如查询某个 repo 下面 issues 的时候，可以通过以下参数来控制返回哪些结果：
    ```json
    state：issue 的状态，可以是 open，closed，all
    since：在指定时间点之后更新过的才会返回
    assignee：被 assign 给某个 user 的 issues
    sort：选择排序的值，可以是 created、updated、comments
    direction：排序的方向，升序（asc）还是降序（desc)
    ```
    例子：

    ```json
    ?limit=10：指定返回记录的数量
    ?offset=10：指定返回记录的开始位置。
    ?page=2&per_page=100：指定第几页，以及每页的记录数。
    ?sortby=name&order=asc：指定返回结果按照哪个属性排序，以及排序顺序。
    ?animal_type_id=1：指定筛选条件
    ```
    + 复杂查询使用post方法
    + 参数的设计允许存在冗余，即允许API路径和URL参数偶尔有重复。比如，GET /zoo/ID/animals 与 GET /animals?zoo_id=ID 的含义是相同的。
+ 资源列表分页标示使用。如果要返回的数目特别多，比如 github 的 /users，就需要使用分页分批次按照需要来返回特定数量的结果。github API 文档中还提到一个很好的点，相关的分页信息还可以存放到 Link 头部，这样客户端可以直接得到诸如下一页、最后一页、上一页等内容的 url 地址

## HTTP交互设计
### HTTP请求方法的使用
+ Get 获取资源
+ Put 新增Store类型；更新资源
+ Post 创建资源，触发控制器类型资源
+ Delete　删除资源
```json
GET（SELECT）：从服务器取出资源（一项或多项）。
POST（CREATE）：在服务器新建一个资源。
PUT（UPDATE）：在服务器更新资源（客户端提供改变后的完整资源）。
PATCH（UPDATE）：在服务器更新资源（客户端提供改变的属性）。
DELETE（DELETE）：从服务器删除资源。
HEAD：获取资源的元数据。
OPTIONS：获取信息，关于资源的哪些属性是客户端可以改变的。
```

例子
```json
GET /zoos：列出所有动物园
POST /zoos：新建一个动物园
GET /zoos/ID：获取某个指定动物园的信息
PUT /zoos/ID：更新某个指定动物园的信息（提供该动物园的全部信息）
PATCH /zoos/ID：更新某个指定动物园的信息（提供该动物园的部分信息）
DELETE /zoos/ID：删除某个动物园
GET /zoos/ID/animals：列出某个指定动物园的所有动物
DELETE /zoos/ID/animals/ID：删除某个指定动物园的指定动物
```

### 响应状态码
404 no found
https://httpstatuses.com/
```latex
200	OK	请求成功接收并处理，一般响应中都会有 body
201	Created	请求已完成，并导致了一个或者多个资源被创建，最常用在 POST 创建资源的时候
202	Accepted	请求已经接收并开始处理，但是处理还没有完成。一般用在异步处理的情况，响应 body 中应该告诉客户端去哪里查看任务的状态
204	No Content	请求已经处理完成，但是没有信息要返回，经常用在 PUT 更新资源的时候（客户端提供资源的所有属性，因此不需要服务端返回）。如果有重要的 metadata，可以放到头部返回
301	Moved Permanently	请求的资源已经永久性地移动到另外一个地方，后续所有的请求都应该直接访问新地址。服务端会把新地址写在 Location 头部字段，方便客户端使用。允许客户端把 POST 请求修改为 GET。
304	Not Modified	请求的资源和之前的版本一样，没有发生改变。用来缓存资源，和条件性请求（conditional request）一起出现
307	Temporary Redirect	目标资源暂时性地移动到新的地址，客户端需要去新地址进行操作，但是不能修改请求的方法。
308	Permanent Redirect	和 301 类似，除了客户端不能修改原请求的方法
400	Bad Request	客户端发送的请求有错误（请求语法错误，body 数据格式有误，body 缺少必须的字段等），导致服务端无法处理
401	Unauthorized	请求的资源需要认证，客户端没有提供认证信息或者认证信息不正确
403	Forbidden	服务器端接收到并理解客户端的请求，但是客户端的权限不足。比如，普通用户想操作只有管理员才有权限的资源。
404	Not Found	客户端要访问的资源不存在，链接失效或者客户端伪造 URL 的时候回遇到这个情况
405	Method Not Allowed	服务端接收到了请求，而且要访问的资源也存在，但是不支持对应的方法。服务端必须返回 Allow 头部，告诉客户端哪些方法是允许的
415	Unsupported Media Type	服务端不支持客户端请求的资源格式，一般是因为客户端在 Content-Type 或者 Content-Encoding 中申明了希望的返回格式，但是服务端没有实现。比如，客户端希望收到 xml返回，但是服务端支持 Json
429	Too Many Requests	客户端在规定的时间里发送了太多请求，在进行限流的时候会用到
500	Internal Server Error	服务器内部错误，导致无法完成请求的内容
503	Service Unavailable	服务器因为负载过高或者维护，暂时无法提供服务。服务器端应该返回 Retry-After 头部，告诉客户端过一段时间再来重试
```
### 元数据
+ HTTP Headers
  + Content-Type：type “/” subtype *（";" parameter）
    + text/html; charest=ISO-8859-4
    + application audio image message model multipart text video
    + REST 一般为 application
    + 可以用查询字段指定客户端希望的类型
  + Location：客户端感兴趣的资源URI
+ body：json，xml，html
  + json是一种流行且轻便友好的格式，json是一种无序的键值对的集合，其中key是需要用双引号引起来的，value如果是数字可以不用双引号，如果是非数字的格式需要使用双引号
+ 错误响应描述: 给出详细的信息

## 授权与验证
如果没有通过验证（提供的用户名和密码不匹配，token 不正确等），需要返回 401 Unauthorized状态码，并在 body 中说明具体的错误信息；而没有被授权访问的资源操作，需要返回 403 Forbidden 状态码，还有详细的错误信息。
http://open.weibo.com/wiki/%E6%8E%88%E6%9D%83%E6%9C%BA%E5%88%B6%E8%AF%B4%E6%98%8E
## 限流rate limit
对用户的请求限流之后，要有方法告诉用户它的请求使用情况，Github API 使用的三个相关的头部：
+ X-RateLimit-Limit: 用户每个小时允许发送请求的最大值
+ X-RateLimit-Remaining：当前时间窗口剩下的可用请求数目
+ X-RateLimit-Rest: 时间窗口重置的时候，到这个时间点可用的请求数量就会变成 X-RateLimit-Limit 的值
如果允许没有登录的用户使用 API（可以让用户试用），可以把 X-RateLimit-Limit 的值设置得很小，比如 Github 使用的 60。没有登录的用户是按照请求的 IP 来确定的，而登录的用户按照认证后的信息来确定身份。
对于超过流量的请求，可以返回 429 Too many requests 状态码，并附带错误信息。而 Github API 返回的是 403 Forbidden，虽然没有 429 更准确，也是可以理解的。

## Hypermedia API
Restful API 的设计最好做到 Hypermedia：在返回结果中提供相关资源的链接。这种设计也被称为 HATEOAS。这样做的好处是，用户可以根据返回结果就能得到后续操作需要访问的地址。

比如访问 api.github.com，就可以看到 Github API 支持的资源操作。

## 编写优秀的文档
https://developer.github.com/v3/
https://developer.paypal.com/docs/api/overview/
# REST开发工具
如上面的图所示，Server统一提供一套RESTful API，web+ios+android作为同等公民调用API。各端发展到现在，都有一套比较成熟的框架来帮开发者事半功倍。
+ -- Server --推荐： Spring MVC 或者 Jersey 或者 Play Framework教程：Getting Started · Building a RESTful Web Service
+ -- Android --推荐： RetroFit ( Retrofit ) 或者 Volley ( mcxiaoke/android-volley · GitHub Google官方的被block，就不贴了 ) 教程：Retrofit โ Getting Started and Create an Android Client快速Android开发系列网络篇之Retrofit
+ -- iOS --推荐：RestKit ( RestKit/RestKit · GitHub )教程：Developing RESTful iOS Apps with RestKit
+ -- Web --推荐随便搞！可以用重量级的AngularJS，也可以用轻量级 Backbone + jQuery 等。教程：http://blog.javachen.com/2015/01/06/build-app-with-spring-boot-and-gradle/
# rest 和 soap
+ rest协议是面向资源的假如要管理一些用户，那么将用户看作是一种资源：
  + get /users/{userId}  获取userId对应的user信息
  + post /users 创建一个新的userput /users/{userId} 更改userId对应的user信息
  + delete /users/{userId} 删除userId对应的user。
+ soap是面向服务的。还是管理用户，将对用户的操作看成服务：
  + post /users/getUser
  + post /users/creatUser
  + post /users/updateUser
  + post /users/deleteUser
