# -*- coding: utf-8 -*-

import os
import argparse
import pickle
import re

Events = ("PushEvent", "IssueCommentEvent", "IssuesEvent", "PullRequestEvent" )
# 四种信息类型
hipping = re.compile(r'"type":"(\w+?)".*?actor.*?"login":"(\S+?)".*?repo.*?"name":"(\S+?)"')
# 使用正则表达式


class inputData:
    def __init__(self):
        self.User = {}
        self.Repo = {}
        self.UserRepo = {}  # 初始化记录读取的内存
    @staticmethod
    def parse(file_path: str):
        records = []  # 从json文件中逐行抽取信息存入空间
        with open(file_path, 'r', encoding='utf-8') as f:  # 打开json文件
            for line in f:
                res = hipping.search(line)  # 运用正则表达式匹配有效数据
                if res is None or res[1] not in Events:
                    continue
                records.append(res.groups())
        return records

    def init(self, dirPath: str):
        records = []
        for curDir, subDir, filenames in os.walk(dirPath):
            filenames = filter(lambda r: r.endswith('.json'), filenames)
            for name in filenames:
                # 将列表扩展拼合
                records.extend(self.parse(f'{curDir}/{name}'))

        for record in records:
            event, user, repo = record
            self.User.setdefault(user, {})
            self.UserRepo.setdefault(user, {})
            self.Repo.setdefault(repo, {})
            self.UserRepo[user].setdefault(repo, {})
            self.User[user][event] = self.User[user].get(event, 0)+1  # 如果不存在就初始化为0，存在就自身+1
            self.Repo[repo][event] = self.Repo[repo].get(event, 0)+1
            self.UserRepo[user][repo][event] = self.UserRepo[user][repo].get(event, 0)+1
        with open('1.json', 'wb') as f:  # 字典转为字符串并将数据写入1、2、3.json
            pickle.dump(self.User, f)
        with open('2.json', 'wb') as f:
            pickle.dump(self.Repo, f)
        with open('3.json', 'wb') as f:
            pickle.dump(self.UserRepo, f)

    def load(self):
        if not any((os.path.exists(f'{i}.json') for i in range(1, 3))):
            raise RuntimeError('error: data file not found')

        with open('1.json', 'rb') as f:
            self.User = pickle.load(f)
        with open('2.json', 'rb') as f:
            self.Repo = pickle.load(f)
        with open('3.json', 'rb') as f:
            self.UserRepo = pickle.load(f)

    def getUser(self, user: str, event: str) -> int:
        return self.User.get(user, {}).get(event, 0)

    def getRepo(self, repo: str, event: str) -> int:
        return self.Repo.get(repo, {}).get(event, 0)

    def getUserRepo(self, user: str, repo: str, event: str) -> int:
        return self.UserRepo.get(user, {}).get(repo, {}).get(event, 0)


class Run:
    # 参数
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.data = None
        self.argInit()

    def argInit(self):
        self.parser.add_argument('-i', '--init', type=str)
        self.parser.add_argument('-u', '--user', type=str)
        self.parser.add_argument('-r', '--repo', type=str)
        self.parser.add_argument('-e', '--event', type=str)

    def analyse(self):
        args = self.parser.parse_args()

        self.data = inputData()
        if args.init:
            self.data.init(args.init)
            return 'init done'
        self.data.load()

        if not args.event:
            raise RuntimeError('error: the following arguments are required: -e/--event')
        if not args.user and not args.repo:
            raise RuntimeError('error: the following arguments are required: -u/--user or -r/--repo')

        if args.user and args.repo:
            res = self.data.getUserRepo(args.user, args.repo, args.event)
        elif args.user:
            res = self.data.getUser(args.user, args.event)
        else:
            res = self.data.getRepo(args.repo, args.event)
        return res


if __name__ == '__main__':
    a = Run()
    print(a.analyse())
