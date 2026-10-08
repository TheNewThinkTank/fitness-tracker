<script module lang="ts">
  export interface ChartPoint { date: string; value: number | null; workoutIds?: string[] }
  export interface ChartSeries { name: string; points: ChartPoint[]; color?: string }
  export interface ChartBand { name: string; start: string; end: string }
</script>

<script lang="ts">
  import { onMount } from "svelte";
  import { init, use, type EChartsType } from "echarts/core";
  import { BarChart, LineChart } from "echarts/charts";
  import { AriaComponent, DataZoomComponent, GridComponent, LegendComponent, MarkAreaComponent, TooltipComponent } from "echarts/components";
  import { CanvasRenderer } from "echarts/renderers";

  use([BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent, MarkAreaComponent, AriaComponent, CanvasRenderer]);

  interface Props {
    title: string;
    unit: string;
    series: ChartSeries[];
    kind?: "line" | "bar";
    onSelect?: (point: ChartPoint) => void;
    bands?: ChartBand[];
  }
  let { title, unit, series, kind = "line", onSelect, bands = [] }: Props = $props();
  let container: HTMLDivElement;
  let chart = $state.raw<EChartsType | null>(null);
  const colors = ["#24766b", "#d95f2b", "#5360a1"];
  const hasData = $derived(series.some((item) => item.points.some((point) => point.value !== null)));

  onMount(() => {
    const instance = init(container, undefined, { renderer: "canvas" });
    chart = instance;
    instance.on("click", (event) => {
      const point = (event.data as { point?: ChartPoint } | undefined)?.point;
      if (point) onSelect?.(point);
    });
    const observer = new ResizeObserver(() => instance.resize());
    observer.observe(container);
    return () => { observer.disconnect(); instance.dispose(); chart = null; };
  });

  $effect(() => {
    if (!chart) return;
    chart.setOption({
      animationDuration: 250,
      textStyle: { fontFamily: "Source Sans 3", color: "#202521" },
      aria: { enabled: true, label: { enabled: true, description: `${title} (${unit})` } },
      grid: { left: 58, right: 20, top: series.length > 1 ? 44 : 20, bottom: 58 },
      tooltip: { trigger: "axis", renderMode: "richText", confine: true },
      legend: { show: series.length > 1, top: 0, type: "scroll" },
      xAxis: {
        type: "time",
        axisLabel: { hideOverlap: true, formatter: (value: number) => new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", timeZone: "UTC" }).format(value) },
        axisLine: { lineStyle: { color: "#b8bcb5" } },
      },
      yAxis: { type: "value", min: 0, axisLabel: { formatter: (value: number) => new Intl.NumberFormat("en-GB", { notation: "compact" }).format(value) }, splitLine: { lineStyle: { color: "#e6e8e2" } } },
      dataZoom: [{ type: "inside", zoomOnMouseWheel: false, moveOnMouseWheel: false }, { type: "slider", height: 16, bottom: 4, borderColor: "#d8d8d0" }],
      series: series.map((item, index) => ({
        name: item.name,
        type: kind,
        connectNulls: false,
        showSymbol: true,
        symbolSize: 6,
        barMaxWidth: 24,
        itemStyle: { color: item.color || colors[index % colors.length] },
        lineStyle: { width: 2 },
        markArea: index === 0 && bands.length ? {
          silent: true,
          label: { show: true, position: "insideTop", fontSize: 10, width: 100, overflow: "truncate", color: "#68706a" },
          data: bands.map((band, bandIndex) => [
            { name: band.name, xAxis: `${band.start}T12:00:00Z`, itemStyle: { color: bandIndex % 2 ? "rgba(83,96,161,0.06)" : "rgba(36,118,107,0.07)" } },
            { xAxis: `${band.end}T12:00:00Z` },
          ]),
        } : undefined,
        data: item.points.map((point) => ({ value: [`${point.date}T12:00:00Z`, point.value], point })),
      })),
    }, true);
  });
</script>

<figure class="metric-chart">
  <figcaption><h3>{title}</h3><span class="unit-label">{unit}</span></figcaption>
  <div class="chart-stage">
    <div class="chart-canvas" bind:this={container} role="img" aria-label={`${title} (${unit})`}></div>
    {#if !hasData}<p class="chart-empty">No eligible measurements</p>{/if}
  </div>
</figure>