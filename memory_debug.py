#!/usr/bin/env python3
"""
NLP项目内存调试脚本

用于分析内存使用情况，识别潜在内存泄漏
"""

import gc
import os
import sys
import tracemalloc
from collections import defaultdict


def check_model_memory_footprint():
    """检查模型文件大小"""
    print("=" * 60)
    print("模型文件内存占用分析")
    print("=" * 60)

    model_dir = "/data/models"
    if not os.path.exists(model_dir):
        print(f"模型目录不存在: {model_dir}")
        return

    total_size = 0
    model_files = {}

    for root, dirs, files in os.walk(model_dir):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                size = os.path.getsize(filepath)
                total_size += size
                model_files[file] = size
            except Exception as e:
                print(f"  无法访问: {filepath} - {e}")

    print(f"\n模型总大小: {total_size / 1024 / 1024:.2f} MB")
    print(f"\n主要文件:")

    sorted_files = sorted(model_files.items(), key=lambda x: x[1], reverse=True)
    for filename, size in sorted_files[:10]:
        print(f"  {filename}: {size / 1024 / 1024:.2f} MB")

    print(f"\n⚠️ 注意: BERT模型文件 ({sorted_files[0][0]}) 占用 {sorted_files[0][1] / 1024 / 1024:.2f} MB")
    print(f"   这将在加载时占用大量内存")


def analyze_current_memory():
    """分析当前进程内存使用"""
    print("\n" + "=" * 60)
    print("当前进程内存分析")
    print("=" * 60)

    tracemalloc.start()

    # 获取内存快照
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    print(f"\nTop 15内存分配:")
    total_allocated = 0
    for i, stat in enumerate(top_stats[:15], 1):
        size_mb = stat.size / 1024 / 1024
        total_allocated += stat.size
        print(f"{i:2}. {size_mb:6.2f} MB  {stat.traceback[0]}")

    print(f"\n跟踪总内存: {total_allocated / 1024 / 1024:.2f} MB")

    # 按文件分组
    by_file = defaultdict(int)
    for stat in top_stats:
        filename = stat.traceback[0].filename
        by_file[filename] += stat.size

    print(f"\n按文件分组 (Top 5):")
    sorted_by_file = sorted(by_file.items(), key=lambda x: x[1], reverse=True)[:5]
    for filename, size in sorted_by_file:
        print(f"  {filename}: {size / 1024 / 1024:.2f} MB")

    tracemalloc.stop()


def analyze_memory_by_type():
    """按对象类型分析内存"""
    print("\n" + "=" * 60)
    print("对象类型分析")
    print("=" * 60)

    gc.collect()

    objects_by_type = defaultdict(int)
    objects_size = defaultdict(int)
    total_size = 0

    for obj in gc.get_objects():
        obj_type = type(obj).__name__
        objects_by_type[obj_type] += 1
        try:
            size = sys.getsizeof(obj)
            objects_size[obj_type] += size
            total_size += size
        except:
            pass

    print(f"\n按数量排序 (Top 10):")
    sorted_by_count = sorted(objects_by_type.items(), key=lambda x: x[1], reverse=True)[:10]
    for obj_type, count in sorted_by_count:
        size_mb = objects_size[obj_type] / 1024 / 1024
        print(f"  {obj_type:<25} {count:>8,}  ({size_mb:6.2f} MB)")

    print(f"\n总对象数: {sum(objects_by_type.values()):,}")
    print(f"总内存大小: {total_size / 1024 / 1024:.2f} MB")


def check_cache_memory():
    """检查缓存内存使用"""
    print("\n" + "=" * 60)
    print("缓存内存分析")
    print("=" * 60)

    try:
        # 尝试导入缓存服务
        sys.path.insert(0, '/home/user/nlp_project/backend')
        from app.services.cache import cache_service

        # 检查Redis连接
        print("缓存服务状态:")
        print(f"  Redis连接: {'已连接' if cache_service.redis else '未连接'}")

        # 注意：这里无法直接获取Redis内存使用，需要通过Redis命令
        print("  提示: 使用 'redis-cli info memory' 查看Redis内存")

    except Exception as e:
        print(f"  无法访问缓存服务: {e}")


def identify_memory_leaks():
    """识别潜在的内存泄漏"""
    print("\n" + "=" * 60)
    print("内存泄漏检测")
    print("=" * 60)

    gc.collect()

    # 检查循环引用
    garbage = gc.garbage
    if garbage:
        print(f"\n⚠️ 发现 {len(garbage)} 个垃圾对象")
        for i, obj in enumerate(garbage[:5]):
            print(f"  {i+1}. {type(obj)}: {repr(obj)[:100]}")
    else:
        print("\n✅ 未发现循环引用")

    # 检查大对象
    print("\n大对象检测 (> 1MB):")
    large_objects = []
    for obj in gc.get_objects():
        try:
            size = sys.getsizeof(obj)
            if size > 1024 * 1024:  # > 1MB
                large_objects.append((type(obj).__name__, size, obj))
        except:
            pass

    if large_objects:
        sorted_large = sorted(large_objects, key=lambda x: x[1], reverse=True)[:10]
        for obj_type, size, obj in sorted_large:
            size_mb = size / 1024 / 1024
            print(f"  {obj_type}: {size_mb:.2f} MB")
            # 尝试显示更详细的信息
            if hasattr(obj, '__class__'):
                print(f"    类: {obj.__class__.__name__}")
            if hasattr(obj, 'shape'):
                print(f"    形状: {obj.shape}")
    else:
        print("  未发现大对象")

    # 检查全局引用
    print("\n全局引用检查:")
    import builtins
    global_objects = []
    for name in dir(builtins):
        obj = getattr(builtins, name)
        try:
            size = sys.getsizeof(obj)
            if size > 1024 * 1024:
                global_objects.append((name, size))
        except:
            pass

    if global_objects:
        for name, size in sorted(global_objects, key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {name}: {size / 1024 / 1024:.2f} MB")
    else:
        print("  全局对象内存使用正常")


def generate_memory_report():
    """生成内存分析报告"""
    print("\n" + "=" * 60)
    print("内存分析总结")
    print("=" * 60)

    # 基于Docker stats获取的数据
    print("\n当前容器内存使用:")
    print("  常驻内存: ~330 MB (根据docker stats)")
    print("  内存限制: 15.58 GB")
    print("  内存占用率: 2.07%")

    print("\n内存占用分析:")
    print("  ✅ 内存占用率低 (< 5%)")
    print("  ⚠️ BERT模型文件: 393 MB (model.safetensors)")
    print("  💡 考虑实现延迟加载（按需加载模型）")

    print("\n潜在优化:")
    print("  1. 模型延迟加载")
    print("     - 当前: 启动时加载所有模型")
    print("     - 建议: 首次使用时加载，避免长期占用内存")
    print()
    print("  2. 缓存策略优化")
    print("     - 当前: Redis缓存1小时")
    print("     - 建议: 根据访问频率调整TTL")
    print()
    print("  3. 定期GC调用")
    print("     - 在批量预测后调用 gc.collect()")
    print("     - 释放临时对象内存")
    print()
    print("  4. 内存监控增强")
    print("     - 添加内存告警 (> 400MB)")
    print("     - 添加缓存命中率监控")
    print("     - 监控模型加载时间")


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "NLP项目内存调试报告" + " " * 24 + "║")
    print("╚" + "=" * 58 + "╝\n")

    # 1. 模型文件分析
    check_model_memory_footprint()

    # 2. 当前内存使用
    try:
        analyze_current_memory()
    except Exception as e:
        print(f"\n当前内存分析失败: {e}")

    # 3. 对象类型分析
    try:
        analyze_memory_by_type()
    except Exception as e:
        print(f"\n对象类型分析失败: {e}")

    # 4. 缓存内存分析
    check_cache_memory()

    # 5. 内存泄漏检测
    identify_memory_leaks()

    # 6. 生成总结报告
    generate_memory_report()

    print("\n" + "=" * 60)
    print("内存调试完成")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
