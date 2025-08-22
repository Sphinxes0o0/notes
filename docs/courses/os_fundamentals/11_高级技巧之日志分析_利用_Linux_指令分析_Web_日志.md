<p>著名的黑客、自由软件运动的先驱理查德.斯托曼说过，“编程不是科学，编程是手艺”。可见，要想真正搞好编程，除了学习理论知识，还需要在实际的工作场景中进行反复的锤炼。</p>



<p>所以今天我们将结合实际的工作场景，带你利用 Linux 指令分析 Web 日志，这其中包含很多小技巧，掌握了本课时的内容，将对你将来分析线上日志、了解用户行为和查找问题有非常大地帮助。</p>
<p>本课时将用到一个大概有 5W 多条记录的nginx日志文件，你可以在<a href="https://github.com/ramroll/lagou-os/blob/main/access.log"> GitHub</a>上下载。 下面就请你和我一起，通过分析这个nginx日志文件，去锤炼我们的手艺。</p>
<h3>第一步：能不能这样做？</h3>
<p>当我们想要分析一个线上文件的时候，首先要思考，能不能这样做？ 这里你可以先用htop指令看一下当前的负载。如果你的机器上没有htop，可以考虑用yum或者apt去安装。</p>
<p><img src="https://s0.lgstatic.com/i/image/M00/5C/7F/CgqCHl-BkJ6AcP32AAduMy8fcSw412.png" alt="Drawing 0.png"></p>


<p>如上图所示，我的机器上 8 个 CPU 都是 0 负载，2G的内存用了一半多，还有富余。 我们用wget将目标文件下载到本地（如果你没有 wget，可以用yum或者apt安装）。</p>
```java
wget 某网址（自己替代）

```
<p>然后我们用ls查看文件大小。发现这只是一个 7M 的文件，因此对线上的影响可以忽略不计。如果文件太大，建议你用scp指令将文件拷贝到闲置服务器再分析。下图中我使用了--block-size让ls以M为单位显示文件大小。</p>
<p><img src="https://s0.lgstatic.com/i/image/M00/5C/74/Ciqc1F-BkKeAQDs9AACqJbZ2jCM025.png" alt="Drawing 1.png"></p>


<p>确定了当前机器的CPU和内存允许我进行分析后，我们就可以开始第二步操作了。</p>
<h3>第二步：LESS 日志文件</h3>
<p>在分析日志前，给你提个醒，记得要less一下，看看日志里面的内容。之前我们说过，尽量使用less这种不需要读取全部文件的指令，因为在线上执行cat是一件非常危险的事情，这可能导致线上服务器资源不足。</p>
<p><img src="https://s0.lgstatic.com/i/image/M00/5C/7F/CgqCHl-BkK6AcDGvAAjaPXe-Nbc605.png" alt="Drawing 2.png"></p>


<p>如上图所示，我们看到nginx的access_log每一行都是一次用户的访问，从左到右依次是：</p>
<ul>
<li>
<p>IP 地址；</p>
</li>
<li>
<p>时间；</p>
</li>
<li>
<p>HTTP 请求的方法、路径和协议版本、返回的状态码；</p>
</li>
<li>
<p>User Agent。</p>
</li>
</ul>
<h3>第三步：PV 分析</h3>
<p>PV（Page View），用户每访问一个页面就是一次Page View。对于nginx的acess_log来说，分析 PV 非常简单，我们直接使用wc -l就可以看到整体的PV。</p>
<p><img src="https://s0.lgstatic.com/i/image/M00/5C/74/Ciqc1F-BkL6AGiY-AABQPMnGu40979.png" alt="Drawing 3.png"></p>




<p>如上图所示：我们看到了一共有 51462 条 PV。</p>
<h3>第四步：PV 分组</h3>
<p>通常一个日志中可能有几天的 PV，为了得到更加直观的数据，有时候需要按天进行分组。为了简化这个问题，我们先来看看日志中都有哪些天的日志。</p>
<p>使用awk '{print $4}' access.log&nbsp; | less可以看到如下结果。awk是一个处理文本的领域专有语言。这里就牵扯到领域专有语言这个概念，英文是Domain Specific Language。领域专有语言，就是为了处理某个领域专门设计的语言。比如awk是用来分析处理文本的DSL，html是专门用来描述网页的DSL，SQL是专门用来查询数据的DSL……大家还可以根据自己的业务设计某种针对业务的DSL。</p>
<p>你可以看到我们用$4代表文本的第 4 列，也就是时间所在的这一列，如下图所示：</p>
<p><img src="https://s0.lgstatic.com/i/image/M00/5C/7F/CgqCHl-BkMaAb421AAGUr-N08hM187.png" alt="Drawing 4.png"></p>


<p>我们想要按天统计，可以利用 awk提供的字符串截取的能力。</p>
<p><img src="https://s0.lgstatic.com/i/image/M00/5C/7F/CgqCHl-BkMuAKo9UAAIcPR902XQ858.png" alt="Drawing 5.png"></p>


<p>上图中，我们使用awk的substr函数，数字2代表从第 2 个字符开始，数字11代表截取 11 个字符。</p>
<p>接下来我们就可以分组统计每天的日志条数了。</p>
<p><img src="https://s0.lgstatic.com/i/image/M00/5C/7F/CgqCHl-BkNGAB-VgAASNmct9nQA628.png" alt="Drawing 6.png"></p>


<p>上图中，使用sort进行排序，然后使用uniq -c进行统计。你可以看到从 2015 年 5 月 17 号一直到 6 月 4 号的日志，还可以看到每天的 PV 量大概是在 2000~3000 之间。</p>
<h3>第五步：分析 UV</h3>
<p>接下来我们分析 UV。UV（Uniq Visitor），也就是统计访问人数。通常确定用户的身份是一个复杂的事情，但是我们可以用 IP 访问来近似统计 UV。</p>
<p><img src="https://s0.lgstatic.com/i/image/M00/5C/74/Ciqc1F-BkNeAam2YAACxCjlKsvc488.png" alt="Drawing 7.png"></p>


<p>上图中，我们使用 awk 去打印$1也就是第一列，接着sort排序，然后用uniq去重，最后用wc -l查看条数。 这样我们就知道日志文件中一共有2660个 IP，也就是2660个 UV。</p>
<h3>第六步：分组分析 UV</h3>
<p>接下来我们尝试按天分组分析每天的 UV 情况。这个情况比较复杂，需要较多的指令，我们先创建一个叫作sum.sh的bash脚本文件，写入如下内容：</p>
```shell
#!/usr/bin/bash
awk '{print substr($4, 2, 11) " " $1}' access.log |\
	sort | uniq |\
	awk '{uv[$1]++;next}END{for (ip in uv) print ip, uv[ip]}'

```
<p>具体分析如下。</p>
<ul>
<li>
<p>文件首部我们使用#!，表示我们将使用后面的/usr/bin/bash执行这个文件。</p>
</li>
<li>
<p>第一次awk我们将第 4 列的日期和第 1 列的ip地址拼接在一起。</p>
</li>
<li>
<p>下面的sort是把整个文件进行一次字典序排序，相当于先根据日期排序，再根据 IP 排序。</p>
</li>
<li>
<p>接下来我们用uniq去重，日期 +IP 相同的行就只保留一个。</p>
</li>
<li>
<p>最后的awk我们再根据第 1 列的时间和第 2 列的 IP 进行统计。</p>
</li>
</ul>
<p>为了理解最后这一行描述，我们先来简单了解下awk的原理。</p>
<p>awk本身是逐行进行处理的。因此我们的next关键字是提醒awk跳转到下一行输入。 对每一行输入，awk会根据第 1 列的字符串（也就是日期）进行累加。之后的END关键字代表一个触发器，就是 END 后面用 {} 括起来的语句会在所有输入都处理完之后执行——当所有输入都执行完，结果被累加到uv中后，通过foreach遍历uv中所有的key，去打印ip和ip对应的数量。</p>
<p>编写完上面的脚本之后，我们保存退出编辑器。接着执行chmod +x ./sum.sh，给sum.sh增加执行权限。然后我们可以像下图这样执行，获得结果：</p>
<p><img src="https://s0.lgstatic.com/i/image/M00/5C/7F/CgqCHl-BkOKAfpNwAAOFk0EhDjU183.png" alt="Drawing 8.png"></p>


<p>如上图，IP地址已经按天进行统计好了。</p>
<h3>总结</h3>
<p>今天我们结合一个简单的实战场景——Web 日志分析与统计练习了之前学过的指令，提高熟练程度。此外，我们还一起学习了新知识——功能强大的awk文本处理语言。在实战中，我们对一个nginx的access_log进行了简单的数据分析，直观地获得了这个网站的访问情况。</p>
<p>我们在日常的工作中会遇到各种各样的日志，除了 nginx 的日志，还有应用日志、前端日志、监控日志等等。你都可以利用今天学习的方法，去做数据分析，然后从中得出结论。</p>
<h3>思考题</h3>
<p>接下来我给你出 2 个场景思考题，帮助你继续练习使用 Linux 指令。</p>
<ol>
<li>
<p>根据今天的 access_log 分析出有哪些终端访问了这个网站，并给出分组统计结果。</p>
</li>
<li>
<p>根据今天的 access_log 分析出访问量 Top 前三的网页。</p>
</li>
</ol>
<p>你可以把你的答案、思路或者课后总结写在留言区，这样可以帮助你产生更多的思考，这也是构建知识体系的一部分。经过长期的积累，相信你会得到意想不到的收获。如果你觉得今天的内容对你有所启发，欢迎分享给身边的朋友。期待看到你的思考！</p>

---
