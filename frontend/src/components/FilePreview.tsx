import React from 'react';
import { FileText, BarChart3 } from 'lucide-react';
import { useAppStore } from '../stores/appStore';

export const FilePreview: React.FC = () => {
  const { session, previewData } = useAppStore();

  if (!session?.file_info || !previewData.length) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>暂无文件预览</p>
        </div>
      </div>
    );
  }

  const { file_info } = session;
  const columns = Object.keys(previewData[0] || {});
  const displayRows = previewData.slice(0, 200); // 最多显示200行

  return (
    <div className="h-full flex flex-col bg-white">
      {/* 文件信息头部 - 扁平化设计带阴影效果 */}
      <div className="mx-4 mt-4 mb-2 px-4 py-3 bg-white rounded-lg shadow-md border-0">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-blue-500" />
              <span className="text-gray-800 font-semibold">{file_info.filename}</span>
            </div>
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4 text-green-500" />
              <span className="text-gray-600 font-medium">{file_info.rows} 行 × {file_info.columns} 列</span>
            </div>
          </div>
          {file_info.rows > 200 && (
            <span className="text-xs text-amber-700 bg-amber-50 px-3 py-1 rounded-full border border-amber-200">
              显示前 200 行
            </span>
          )}
        </div>
      </div>

      {/* 表格预览 */}
      <div className="flex-1 overflow-auto bg-gray-50">
        <div className="w-full p-4">
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto">
              <thead className="bg-blue-50">
                <tr>
                  <th className="w-16 px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">
                    #
                  </th>
                  {columns.map((column, index) => (
                    <th
                      key={index}
                      className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase"
                    >
                      <div className="truncate" title={column}>
                        {column}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {displayRows.map((row, rowIndex) => (
                  <tr
                    key={rowIndex}
                    className="hover:bg-blue-50 transition-colors duration-150"
                  >
                    <td className="px-4 py-3 text-sm text-gray-500 font-mono bg-gray-50">
                      {rowIndex + 1}
                    </td>
                    {columns.map((column, colIndex) => (
                      <td
                        key={colIndex}
                        className="px-4 py-3 text-sm text-gray-900"
                      >
                        <div className="truncate" title={String(row[column] || '')}>
                          {row[column] !== null && row[column] !== undefined 
                            ? String(row[column]) 
                            : <span className="text-gray-400 italic">-</span>
                          }
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </div>
        </div>
      </div>

      {/* 底部统计信息 */}
      <div className="p-4 bg-gradient-to-r from-gray-50 to-gray-100">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 font-medium">
            显示 {displayRows.length} / {file_info.rows.toLocaleString()} 行数据
          </span>
          {file_info.rows > displayRows.length && (
            <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-medium">
              已截取前 {displayRows.length} 行
            </span>
          )}
        </div>
      </div>
    </div>
  );
};