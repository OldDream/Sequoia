微信push似乎不行了，采用钉钉群 + 机器人 + webhook 进行推送。

```
import requests
import json
 
class DingTalk_Base:
    def __init__(self):
        self.__headers = {'Content-Type': 'application/json;charset=utf-8'}
        self.url = 'https://oapi.dingtalk.com/robot/send?access_token=52e803a459a17146d3a051ad4d3ca9e833f09e2628ea3a06a459cb97627da8c7'
 
    def send_msg(self, text):
        json_text = {
                "msgtype": "text",
                "text": {
                "content": "测试:123"            ## 写入要传送的内容
            },
                "at": {
                "atMobiles": [""],
                "isAtAll": False
            }
        }
        return requests.post(self.url, json.dumps(json_text), headers=self.__headers).content
 
 
class DingTalk_Disaster(DingTalk_Base):
    def __init__(self):
        super().__init__()
        # 填写机器人的url
        self.url = 'https://oapi.dingtalk.com/robot/send?access_token=52e803a459a17146d3a051ad4d3ca9e833f09e2628ea3a06a459cb97627da8c7'
 
if __name__ == '__main__':
    ding = DingTalk_Disaster()
    ding.send_msg('')
```