from csv import DictReader

from matplotlib import pyplot as plt

from utils.downloader.rate_control.rate_control import RateControl


def draw_analyse():
    with open(RateControl.record_file, 'w', newline='') as csvfile:
        fail_rate_recode = []
        tasks_num_recode = []

        # 读取数据
        reader: DictReader = DictReader(csvfile)
        for row in reader:
            fail_rate_recode.append(row[RateControl.fail_rate_key])
            tasks_num_recode.append(row[RateControl.tasks_num_key])

        # 绘图
        fig = plt.figure()
        plot1 = fig.add_subplot()

        x = range(len(fail_rate_recode))

        plot1.plot(x, fail_rate_recode, '-', label="fail_rate", color='r')
        plot1.legend()

        plot2 = plot1.twinx()
        plot2.plot(x, tasks_num_recode, '-', label="tasks_num", color='b')
        plot2.legend()
        plt.show()