import React from 'react'
import { diffWords } from 'diff'

const TextDiff = ({ original, humanized }) => {
  const diff = diffWords(original, humanized)

  return (
    <div className="p-4 bg-gray-50 rounded-lg max-h-96 overflow-y-auto">
      {diff.map((part, index) => (
        <span
          key={index}
          className={
            part.added
              ? 'bg-green-200 text-green-900'
              : part.removed
              ? 'bg-red-200 text-red-900 line-through'
              : ''
          }
        >
          {part.value}
        </span>
      ))}
    </div>
  )
}

export default TextDiff