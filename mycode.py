import time
import threading
import logging
from queue import Queue, Empty
import schedule
from flask import Flask, request
import requests
import os
import webbrowser
import click

# ================= 日志配置 =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)
click.echo = lambda message=None, file=None, nl=True, err=False, color=None: None
logging.getLogger('werkzeug').disabled = True
logging.getLogger('flask.app').disabled = True

# ================= 共享状态 =================
class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.latest_data = None
        self.need_rerun = False

    def update_data(self, data):
        with self.lock:
            self.latest_data = data

    def mark_need_rerun(self, val):
        with self.lock:
            self.need_rerun = val

    def snapshot(self):
        with self.lock:
            return self.latest_data, self.need_rerun


state = SharedState()

# ================= 执行签到 =================
def handler(data):
    host = 'https://api-cloudgame.mihoyo.com'
    headers = data.get('headers')

    logger.info("开始获取钱包余额...")
    resp = requests.get(
        f'{host}/hk4e_cg_cn/wallet/wallet/get',
        headers=headers
    )
    wallet_data = resp.json()

    if wallet_data.get("retcode") == -100:
        return False

    free_time = wallet_data["data"]["free_time"]["free_time"]
    play_card_msg = wallet_data["data"]["play_card"]["short_msg"]
    coin_num = wallet_data["data"]["coin"]["coin_num"]
    coin_minutes = int(coin_num) / 10 if coin_num is not None else 0

    logger.info(
        f"钱包：免费时长 {free_time} 分钟，"
        f"畅玩卡状态「{play_card_msg}」，"
        f"原点 {coin_num} 点（约 {coin_minutes:.0f} 分钟）"
    )
    
    logger.info("开始尝试领取奖励...")
    resp = requests.get(
        f'{host}/hk4e_cg_cn/gamer/api/listNotifications'
        f'?status=NotificationStatusUnread'
        f'&type=NotificationTypePopup&is_sort=true',
        headers=headers
    )

    notification_list = resp.json()['data'].get('list', [])

    if not notification_list:
        logger.info("今天似乎已经签到过了...")
    else:
        for n in notification_list:
            reward_id = n['id']
            minutes = n['num']
            msg = n['msg']

            requests.post(
                f'{host}/hk4e_cg_cn/gamer/api/ackNotification',
                json={"id": reward_id},
                headers=headers
            )

            logger.info(f"领取奖励成功：{msg}，获得 {minutes} 分钟")

    return True


# ================= 任务队列 =================
task_q: "Queue[dict]" = Queue(maxsize=1)
q_lock = threading.Lock()


def enqueue_latest(data):
    with q_lock:
        try:
            while True:
                task_q.get_nowait()
        except Empty:
            pass

        task_q.put_nowait(data)


def worker_loop():
    while True:
        data = task_q.get()
        logger.info("开始执行今日的签到任务！")

        ok = bool(handler(data))
        state.mark_need_rerun(not ok)

        if ok:
            logger.info("今日的签到任务执行完成！")
        else:
            logger.warning("登录状态已失效，请重新登录！如果打开的是安装了所需油猴脚本的浏览器，直接登录即可！")
            webbrowser.open('https://ys.mihoyo.com/cloud/#/')

        task_q.task_done()


# ================= Flask 服务 =================
app = Flask(__name__)
app.logger.disabled = True


@app.post("/push")
def push():
    data = request.get_json(silent=True)
    if data is not None:
        latest_data, need_rerun = state.snapshot()
        if data != latest_data:
            logger.info("已更新登录状态！")
            state.update_data(data)
            if need_rerun:
                enqueue_latest(data)
    return "", 200


def run_flask(host, port):
    app.run(
        host=host,
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True
    )


# ================= 定时任务 =================
def job():
    latest_data, _ = state.snapshot()

    if latest_data is None:
        logger.warning("没有登录信息，请重新登录！如果打开的是安装了所需油猴脚本的浏览器，直接登录即可！")
        webbrowser.open('https://ys.mihoyo.com/cloud/#/')
        state.mark_need_rerun(True)
        return

    enqueue_latest(latest_data)


# ================= 主入口 =================
def main():
    threading.Thread(target=worker_loop, daemon=True).start()

    threading.Thread(
        target=run_flask,
        kwargs={"host": "127.0.0.1", "port": 5000},
        daemon=True
    ).start()

    schedule.every().day.at("07:00").do(job)

    logger.info("程序启动成功，将在每天 07:00 执行签到任务")

    job()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()