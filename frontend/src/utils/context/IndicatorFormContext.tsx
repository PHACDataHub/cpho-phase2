import { createContext } from "react";
import { ErrorType, IndicatorType } from "../types";

type IndicatorFormContextType = {
  indicator?: IndicatorType;
  setField: (field: string, value: any) => void;
  addBlankDataPoint: () => void;
  editDataPoint: (uuid: string, field: string, value: any) => void;
  replaceDataPoint: (uuid: string, newDataPoint: any) => void;
  addDataPoint: (newDataPoint: any) => void;
  deleteDataPoint: (uuid: string) => void;
  duplicateDataPoint: (uuid: string) => void;
  errors: ErrorType[];
  addError: (error: ErrorType) => void;
  removeError: (field: string, dataPointId: string) => void;
  clearRowErrors: (dataPointId: string) => void;
  step: number;
  setStep: (step: number) => void;
};

const IndicatorFormContext = createContext<IndicatorFormContextType>({
  setField: () => {},
  addBlankDataPoint: () => {},
  editDataPoint: () => {},
  replaceDataPoint: () => {},
  addDataPoint: () => {},
  deleteDataPoint: () => {},
  duplicateDataPoint: () => {},
  errors: [],
  addError: () => {},
  removeError: () => {},
  clearRowErrors: () => {},
  step: 0,
  setStep: () => {},
});

export const IndicatorFormProvider = IndicatorFormContext.Provider;

export default IndicatorFormContext;
