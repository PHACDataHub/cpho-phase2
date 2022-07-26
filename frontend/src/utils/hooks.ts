import { useEffect, useState } from "react";
import { IndicatorDataFields } from "./constants";

export const useSmallScreen = () => {
  const [smallScreen, setSmallScreen] = useState(false);
  useEffect(() => {
    const handleResize = () => {
      setSmallScreen(window.innerWidth < 768);
    };
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);
  return smallScreen;
};

export const getCleanPTName = (name: string) => {
  return IndicatorDataFields.find(
    (field) => field.id === "dp_location"
  )?.options?.find((option) => option.value === name)?.label;
};
