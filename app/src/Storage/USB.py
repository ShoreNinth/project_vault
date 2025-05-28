import usb.core
import usb.util

import os
import subprocess
import shutil
import time
import psutil
import usb.core
import sys

# # U盘设备信息
class USBID:

    VENDOR_ID = 0x0000
    PRODUCT_ID = 0x0000

def find_usb_device():
    """查找U盘设备"""
    devices = usb.core.find(find_all=True)
    for device in devices:
        # 检查设备的每个配置
        for cfg in device:
            # 检查配置的每个接口
            for intf in cfg:
                # 检查接口类别是否为0x08 (Mass Storage)
                if intf.bInterfaceClass == 0x08:
                    USBID.VENDOR_ID = device.idVendor
                    USBID.PRODUCT_ID = device.idProduct
                    break  # 找到即跳出当前配置的循环

    device = usb.core.find(idVendor=USBID.VENDOR_ID, idProduct=USBID.PRODUCT_ID)
    print("Found USB device")
    if device is None:
        raise ValueError("未找到U盘设备，请确保U盘已插入")
    return device


def get_device_node():
    """获取U盘设备节点"""
    return f"/dev/sda1"
    # # 通过lsblk命令获取设备信息
    # result = subprocess.run(['lsblk', '-o', 'NAME,VENDOR,MODEL,MOUNTPOINT', '-d'],
    #                         capture_output=True, text=True)
    #
    # # 查找包含我们U盘信息的行
    # for line in result.stdout.splitlines():
    #     if f"{VENDOR_ID:04x}" in line.lower() and f"{PRODUCT_ID:04x}" in line.lower():
    #         parts = line.split()
    #         if parts:
    #             device_name = parts[0]
    #             return f"/dev/{device_name}"


    # # 尝试通过USB路径查找
    # try:
    #     device = find_usb_device()
    #     bus_id = f"{device.bus:03d}"
    #     dev_id = f"{device.address:03d}"
    #
    #     # 在/sys/bus/usb/devices中查找对应的设备
    #     usb_path = f"/sys/bus/usb/devices/{bus_id}-{dev_id}"
    #     if os.path.exists(usb_path):
    #         for entry in os.listdir(usb_path):
    #             if entry.startswith(bus_id) and ":" in entry:
    #                 scsi_path = os.path.join(usb_path, entry)
    #                 block_path = os.path.join(scsi_path, "block")
    #                 if os.path.exists(block_path):
    #                     device_name = os.listdir(block_path)[0]
    #                     return f"/dev/{device_name}"
    # except Exception:
    #     pass
    #
    # raise ValueError("无法确定U盘设备节点，请尝试手动挂载")


def is_mounted(device_node):
    """检查设备是否已挂载"""
    partitions = psutil.disk_partitions()
    for p in partitions:
        if p.device == device_node:
            return p.mountpoint
    return None


def mount_usb(device_node, mount_point="/mnt/usb"):
    """挂载U盘"""
    # 确保挂载点存在
    os.makedirs(mount_point, exist_ok=True)

    # 尝试挂载（支持NTFS和FAT32）
    try:
        # 首先尝试NTFS挂载
        subprocess.run(['sudo', 'mount', '-t', 'ntfs', device_node, mount_point],
                       check=True)
        print(f"已挂载NTFS文件系统到 {mount_point}")
    except subprocess.CalledProcessError:
        try:
            # 如果NTFS失败，尝试FAT32
            subprocess.run(['sudo', 'mount', '-t', 'vfat', device_node, mount_point],
                           check=True)
            print(f"已挂载FAT32文件系统到 {mount_point}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"挂载失败: {e}") from e

    return mount_point


def unmount_usb(mount_point):
    """卸载U盘"""
    try:
        subprocess.run(['sudo', 'umount', mount_point], check=True)
        print(f"已卸载 {mount_point}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"卸载失败: {e}") from e


def write_key(mount_point, split_key:str):
    """在U盘上进行读写测试"""
    test_file = os.path.join(mount_point, "shamir_split_key.txt")

    # 写入文件

    with open(test_file, 'w') as f:
        f.write(split_key)
        f.write("\n")
        f.write(f"创建时间: {time.ctime()}\n")


def main():
    print("=== U盘文件读写操作 ===")

    try:
        # 1. 查找U盘设备
        print("\n步骤1: 查找U盘设备...")
        device = find_usb_device()
        print(f"找到U盘: ID {device.idVendor:04x}:{device.idProduct:04x}")
        print(f"总线: {device.bus}, 地址: {device.address}")

        # 2. 获取设备节点
        print("\n步骤2: 获取设备节点...")
        device_node = get_device_node()
        print(f"设备节点: {device_node}")

        # 3. 检查挂载状态
        print("\n步骤3: 检查挂载状态...")
        mount_point = is_mounted(device_node)
        if mount_point:
            print(f"U盘已挂载在: {mount_point}")
        else:
            print("U盘未挂载，尝试挂载...")
            mount_point = mount_usb(device_node)

        # 4. 进行文件读写测试
        print("\n步骤4: 进行文件读写测试...")
        write_key(mount_point, "这里是密钥分片")

        print("\n操作完成！")

    except Exception as e:
        print(f"\n错误: {e}")
        print("请检查: ")
        print("1. U盘是否已插入")
        print("2. 是否有NTFS支持 (sudo apt install ntfs-3g)")
        print("3. 是否有足够的权限 (尝试使用sudo运行脚本)")
        sys.exit(1)

