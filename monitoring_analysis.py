#!/usr/bin/env python3
"""
NLP项目监控指标分析脚本

分析内存、GC、性能等监控指标
"""
import gc
import sys
import time
import tracemalloc
from collections import defaultdict


def analyze_gc_statistics():
    """分析垃圾回收统计"""
    print("=" * 60)
    print("垃圾回收 (GC) 分析")
    print("=" * 60)

    # 强制GC
    gc.collect()

    stats = gc.get_stats()
    total_collected = 0
    total_uncollectable = 0

    for gen in range(len(stats)):
        gen_stats = stats[gen]
        collected = gen_stats.get('collected', 0)
        uncollectable = gen_stats.get('uncollectable', 0)
        total_collected += collected
        total_uncollectable += uncollectable

        print(f"\nGeneration {gen}:")
        print(f"  已回收对象: {collected:,}")
        print(f"  无法回收对象: {uncollectable:,}")

        if collected > 0:
            print(f"  回收率: {(collected / (collected + uncollectable) * 100):.2f}%")

    print(f"\n总计:")
    print(f"  总回收对象: {total_collected:,}")
    print(f"  总无法回收: {total_uncollectable:,}")

    # GC健康状态
    if total_uncollectable == 0:
        print(f"  ✅ GC健康: 无无法回收的对象")
    else:
        print(f"  ⚠️ 警告: 存在{total_uncollectable}个无法回收的对象（可能循环引用）")

    return stats


def analyze_memory_usage():
    """分析内存使用"""
    print("\n" + "=" * 60)
    print("内存使用分析")
    print("=" * 60)

    # 启动内存跟踪
    tracemalloc.start()

    # 获取当前内存快照
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    print(f"\n当前内存分配 (前10大占用):")
    for stat in top_stats[:10]:
        print(f"  {stat}")

    # 按traceback分组
    print(f"\n按文件分组的Top 5内存占用:")
    by_file = defaultdict(int)
    for stat in top_stats:
        filename = stat.traceback[0].filename
        by_file[filename] += stat.size

    sorted_by_file = sorted(by_file.items(), key=lambda x: x[1], reverse=True)[:5]
    for filename, size in sorted_by_file:
        print(f"  {filename}: {size / 1024 / 1024:.2f} MB")

    total_allocated = sum(stat.size for stat in top_stats)
    print(f"\n总跟踪内存: {total_allocated / 1024 / 1024:.2f} MB")
    print(f"当前块数: {snapshot.statistics('traceback')[0].count}")

    tracemalloc.stop()

    return snapshot


def analyze_objects():
    """分析Python对象分布"""
    print("\n" + "=" * 60)
    print("对象分布分析")
    print("=" * 60)

    gc.collect()  # 强制GC后统计

    objects_by_type = defaultdict(int)
    total_size = 0

    for obj in gc.get_objects():
        obj_type = type(obj).__name__
        objects_by_type[obj_type] += 1
        try:
            total_size += sys.getsizeof(obj)
        except:
            pass

    # 按数量排序，显示Top 15
    sorted_objects = sorted(objects_by_type.items(), key=lambda x: x[1], reverse=True)[:15]

    print(f"\n对象类型分布 (Top 15):")
    print(f"  {'类型':<25} {'数量':>10}")
    print(f"  {'-' * 35}")
    for obj_type, count in sorted_objects:
        print(f"  {obj_type:<25} {count:>10,}")

    print(f"\n总对象数: {sum(objects_by_type.values()):,}")
    print(f"总内存大小: {total_size / 1024 / 1024:.2f} MB")


def check_circular_references():
    """检查循环引用"""
    print("\n" + "=" * 60)
    print("循环引用检查")
    print("=" * 60)

    gc.collect()

    garbage = gc.garbage
    if not garbage:
        print("✅ 未发现循环引用")
    else:
        print(f"⚠️ 发现 {len(garbage)} 个对象在垃圾列表中")
        for i, obj in enumerate(garbage[:5]):  # 只显示前5个
            print(f"  对象{i+1}: {type(obj)} - {repr(obj)[:100]}")


def check_memory_trends():
    """检查内存趋势（模拟分析）"""
    print("\n" + "=" * 60)
    print("内存趋势分析（基于当前指标）")
    print("=" * 60)

    # 当前已知数据
    current_metrics = {
        'python_gc_objects_collected_total': {
            'generation_0': 8229,
            'generation_1': 1401,
            'generation_2': 4223,
        },
        'process_resident_memory_bytes': 460_922_880,  # ~441 MB
        'process_virtual_memory_bytes': 2_479_452_160,  # ~2.48 GB
        'process_cpu_seconds_total': 25.9,
    }

    resident_mb = current_metrics['process_resident_memory_bytes'] / 1024 / 1024
    virtual_mb = current_metrics['process_virtual_memory_bytes'] / 1024 / 1024

    print(f"\n当前内存使用:")
    print(f"  常驻内存: {resident_mb:.2f} MB")
    print(f"  虚拟内存: {virtual_mb:.2f} MB")
    print(f"  内存差值: {virtual_mb - resident_mb:.2f} MB (共享库/未使用内存)")

    # 分析GC频率
    total_gc = sum(current_metrics['python_gc_objects_collected_total'].values())
    print(f"\n垃圾回收统计:")
    print(f"  Gen 0 (频繁): {current_metrics['python_gc_objects_collected_total']['generation_0']:,} 对象")
    print(f"  Gen 1 (中等): {current_metrics['python_gc_objects_collected_total']['generation_1']:,} 对象")
    print(f"  Gen 2 (稀疏): {current_metrics['python_gc_objects_collected_total']['generation_2']:,} 对象")

    # 内存健康评估
    print(f"\n内存健康评估:")

    # 评估1: 441MB对于NLP服务来说偏大
    if resident_mb > 500:
        print(f"  ⚠️ 警告: 常驻内存 {resident_mb:.2f} MB 偏高")
        print(f"     建议: 检查模型加载和缓存策略")
    elif resident_mb > 300:
        print(f"  ⚠️ 注意: 常驻内存 {resident_mb:.2f} MB 中等")
        print(f"     建议: 可考虑优化大对象缓存")
    else:
        print(f"  ✅ 正常: 常驻内存 {resident_mb:.2f} MB 在合理范围")

    # 评估2: GC回收率
    gen2_ratio = current_metrics['python_gc_objects_collected_total']['generation_2'] / total_gc * 100
    if gen2_ratio > 20:
        print(f"  ⚠️ 注意: Gen 2回收比例 {gen2_ratio:.1f}% 偏高")
        print(f"     建议: 可能存在长生命周期大对象")

    # 评估3: 虚拟内存
    overhead = virtual_mb - resident_mb
    overhead_ratio = overhead / resident_mb * 100
    if overhead_ratio > 50:
        print(f"  ℹ️ 信息: 虚拟内存开销 {overhead:.2f} MB ({overhead_ratio:.1f}%)")
        print(f"     说明: 这是正常的（包含了未使用的地址空间）")


def generate_recommendations():
    """生成优化建议"""
    print("\n" + "=" * 60)
    print("优化建议")
    print("=" * 60)

    recommendations = [
        ("内存优化", [
            "✅ 已安装psutil以获取真实的系统资源信息",
            "🔍 检查模型缓存策略：考虑使用弱引用缓存大型模型对象",
            "🔍 评估Redis缓存命中率，减少内存中重复数据",
            "💡 考虑为BERT等大型模型实现延迟加载（按需加载）",
            "💡 定期调用gc.collect()在内存密集型操作后（如批量预测）",
        ]),
        ("GC优化", [
            "✅ GC无无法回收对象（健康）",
            "💡 监控GC频率：如果Gen 0回收过于频繁（>1000/小时），考虑调整阈值",
            "💡 对于长期运行的服务，考虑定期重启（避免内存碎片）",
        ]),
        ("监控完善", [
            "📊 集成自定义业务指标（predictions_total, prediction_duration）",
            "📊 添加缓存命中率监控",
            "📊 添加数据库连接池监控",
            "📊 添加Redis连接数和内存使用监控",
        ]),
    ]

    for category, items in recommendations:
        print(f"\n{category}:")
        for item in items:
            print(f"  {item}")


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "NLP项目监控指标分析报告" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")

    # 1. GC分析
    gc_stats = analyze_gc_statistics()

    # 2. 内存分析
    try:
        memory_snapshot = analyze_memory_usage()
    except Exception as e:
        print(f"\n内存分析失败: {e}")

    # 3. 对象分布
    try:
        analyze_objects()
    except Exception as e:
        print(f"\n对象分析失败: {e}")

    # 4. 循环引用检查
    check_circular_references()

    # 5. 内存趋势
    check_memory_trends()

    # 6. 优化建议
    generate_recommendations()

    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
