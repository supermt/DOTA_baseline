import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
    df = pd.read_csv("tables/compaction_time_line.csv")
    # fig = plt.figure(figsize=(20,9))
    ax = plt.subplot(511)
    ax1 = plt.subplot(512)
    ax2 = plt.subplot(513)
    ax3 = plt.subplot(514)
    ax4 = plt.subplot(515)

    ax.plot(df["microseconds"],df["Read Speed (MB/s)"],color="red",label="Read Speed (MB/s)")
    ax1.plot(df["microseconds"],df["Write Speed (MB/s)"],color="blue",label="Write Speed (MB/s)")
    ax2.plot(df["microseconds"],df["Input File Size (Input Level)"]+df["Input File Size (Output Level)"],color="green",label="Input File Size")
    ax3.plot(df["microseconds"],df["Output File Size (MB)"],color="black",label="Output File Size")
    ax4.plot(df["microseconds"])

    plt.show()
