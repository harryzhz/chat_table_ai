import React, { useState, useRef, useCallback } from 'react';

interface ResizablePanelsProps {
  leftPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  defaultLeftWidth?: number; // 百分比，默认33%
  minLeftWidth?: number; // 最小宽度百分比，默认20%
  maxLeftWidth?: number; // 最大宽度百分比，默认80%
}

export const ResizablePanels: React.FC<ResizablePanelsProps> = ({
  leftPanel,
  rightPanel,
  defaultLeftWidth = 33,
  minLeftWidth = 20,
  maxLeftWidth = 80,
}) => {
  const [leftWidth, setLeftWidth] = useState(defaultLeftWidth);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging || !containerRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();
      const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
      
      // 限制在最小和最大宽度之间
      const clampedWidth = Math.max(minLeftWidth, Math.min(maxLeftWidth, newLeftWidth));
      setLeftWidth(clampedWidth);
    },
    [isDragging, minLeftWidth, maxLeftWidth]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // 添加全局鼠标事件监听
  React.useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div ref={containerRef} className="flex-1 flex overflow-hidden">
      {/* 左侧面板 */}
      <div 
        className="bg-white overflow-hidden"
        style={{ width: `${leftWidth}%` }}
      >
        {leftPanel}
      </div>

      {/* 可拖拽的分割线 */}
      <div
        className={`
          relative flex-shrink-0 w-1 bg-gray-200 cursor-col-resize
          hover:bg-blue-400 transition-colors duration-200
          ${isDragging ? 'bg-blue-500' : ''}
        `}
        onMouseDown={handleMouseDown}
      >
        {/* 分割线中间的拖拽指示器 */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className={`
            w-1 h-8 bg-gray-400 rounded-full
            ${isDragging ? 'bg-blue-600' : 'hover:bg-blue-500'}
            transition-colors duration-200
          `} />
        </div>
        
        {/* 悬停时显示的提示 */}
        <div className={`
          absolute top-1/2 left-2 transform -translate-y-1/2
          bg-gray-800 text-white text-xs px-2 py-1 rounded
          opacity-0 pointer-events-none transition-opacity duration-200
          ${isDragging ? 'opacity-100' : 'hover:opacity-100'}
          whitespace-nowrap z-10
        `}>
          拖拽调整宽度
        </div>
      </div>

      {/* 右侧面板 */}
      <div 
        className="bg-white overflow-hidden"
        style={{ width: `${100 - leftWidth}%` }}
      >
        {rightPanel}
      </div>
    </div>
  );
};