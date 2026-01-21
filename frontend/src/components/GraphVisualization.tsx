'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { GraphData, GraphNode } from '@/lib/api';

interface Props {
  data: GraphData;
  onNodeClick?: (node: GraphNode) => void;
}

export function GraphVisualization({ data, onNodeClick }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 600;

    svg.attr('viewBox', [0, 0, width, height]);

    // Color by type
    const colorScale = d3.scaleOrdinal<string>()
      .domain(['Card', 'Mechanic', 'Role'])
      .range(['#4299e1', '#48bb78', '#ed8936']);

    // Create simulation
    const simulation = d3.forceSimulation(data.nodes as d3.SimulationNodeDatum[])
      .force('link', d3.forceLink(data.edges)
        .id((d: d3.SimulationNodeDatum) => (d as GraphNode).id)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Draw edges
    const link = svg.append('g')
      .selectAll('line')
      .data(data.edges)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2);

    // Draw nodes
    const node = svg.append('g')
      .selectAll('g')
      .data(data.nodes)
      .join('g')
      .style('cursor', 'pointer')
      .on('click', (_, d) => onNodeClick?.(d))
      .call(d3.drag<any, any>()
        .on('start', (event: any, d: any) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event: any, d: any) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event: any, d: any) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }));

    node.append('circle')
      .attr('r', d => d.type === 'Card' ? 20 : 15)
      .attr('fill', d => colorScale(d.type));

    node.append('text')
      .text(d => d.label.length > 15 ? d.label.slice(0, 12) + '...' : d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', 30)
      .attr('font-size', 10);

    simulation.on('tick', () => {
      link
        .attr('x1', (d) => (d.source as d3.SimulationNodeDatum).x!)
        .attr('y1', (d) => (d.source as d3.SimulationNodeDatum).y!)
        .attr('x2', (d) => (d.target as d3.SimulationNodeDatum).x!)
        .attr('y2', (d) => (d.target as d3.SimulationNodeDatum).y!);

      node.attr('transform', (d) => `translate(${(d as d3.SimulationNodeDatum).x},${(d as d3.SimulationNodeDatum).y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [data, onNodeClick]);

  return (
    <svg ref={svgRef} className="w-full h-[600px] border rounded bg-gray-50" />
  );
}
