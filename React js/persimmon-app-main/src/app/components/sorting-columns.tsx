import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSortUp, faSortDown } from '@fortawesome/free-solid-svg-icons';

interface SortableColumnProps {
  label: string;
  sortKey: string;
  sortingOrder: { [key: string]: number };
  onSort: (key: string) => void;
}

const SortableColumn: React.FC<SortableColumnProps> = ({ label, sortKey, sortingOrder, onSort }) => {
  return (
    <span className="flex items-center">
      {label}
      <span className="flex flex-col items-center ml-1" onClick={() => onSort(sortKey)}>
        <FontAwesomeIcon
          icon={faSortUp}
          width={12}
          height={14.4}
          className={`cursor-pointer ${sortingOrder[sortKey] === 1 ? 'text-black' : 'text-slate-200'}`}
        />
        <FontAwesomeIcon
          icon={faSortDown}
          width={12}
          height={14.4}
          className={`cursor-pointer -mt-3 ${sortingOrder[sortKey] === 2 ? 'text-black' : 'text-slate-200'}`}
        />
      </span>
    </span>
  );
};

export default SortableColumn;
