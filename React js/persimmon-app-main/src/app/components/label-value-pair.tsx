import React from 'react';

interface LabelValuePairProps {
  label: string;
  value: string | number | null | undefined | React.ReactNode;
  labelClassName?: string;
  valueClassName?: string;
  containerClassName?: string;
}

const LabelValuePair: React.FC<LabelValuePairProps> = ({
  label,
  value,
  labelClassName = "",
  valueClassName = "",
  containerClassName = "",
}) => {
  return (
    <div className={containerClassName}>
      <p className={labelClassName}>{label}</p>
      <p className={valueClassName}>
        {value || "N/A"}
      </p>
    </div>
  );
};

export default LabelValuePair;

