import dynamic from "next/dynamic";
import { useState, useEffect } from "react";

// Dynamically import ApexCharts to avoid SSR issues
const ReactApexChart = dynamic(() => import("react-apexcharts"), { ssr: false });

interface SpeedometerProps {
  score: number; // Score percentage (0-100)
}

export default function Speedometer({ score }: SpeedometerProps) {
  const [options, setOptions] = useState({});
  const [series, setSeries] = useState([0]);

  useEffect(() => {
    // Define options for the speedometer gauge
    setOptions({
      chart: {
        type: "radialBar",
      },
      plotOptions: {
        radialBar: {
          startAngle: -90,
          endAngle: 90,
          hollow: {
            margin: 15,
            size: "70%",
          },
          dataLabels: {
            name: {
              offsetY: 10, // Adjusted to position below the half circle
              color: "#888",
              fontSize: "20px",
            },
            value: {
              fontSize: "24px", // Increased font size for better visibility
              show: false,
              formatter: function (val: number) {
                return `${val}%`;
              },
            },
          },
        },
      },
      fill: {
        type: "solid",
        colors: ["#0891B2"], // Filled color
      },
      stroke: {
        lineCap: "round",
        colors: ["#7E8FA7"]
      },
      labels: [""],
    });

    // Set the score for the speedometer
    setSeries([score]);
  }, [score]);
  const getMatchQuality = (score: number) => {
    if (score >= 86) return "Excellent"
    if (score >= 71) return "Good"
    if (score >= 46) return "Fair"
    return "Poor"
  }
  return (
    <div className="flex justify-center items-center">
      <div className="relative flex flex-col items-center">
        <ReactApexChart options={options} series={series} type="radialBar" height={200} />
        <div className="absolute top-1/2 transform -translate-y-1/2 text-center" style={{ marginTop: '0px' }}>
          <span className="text-2xl font-bold text-black">{score}%</span> {/* Display the score in the center */}
        </div>
        <div className="mt-[-40px] text-sm">{getMatchQuality(score)} Match</div>
      </div>
      <style jsx>{`
        .apexcharts-radius {
          stroke: #7E8FA7; /* Color for the empty part of the bar */
        }
      `}</style>
    </div>
  );
}
