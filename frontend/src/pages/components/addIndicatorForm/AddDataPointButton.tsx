import { HamburgerIcon } from "@chakra-ui/icons";
import { Button, useDisclosure } from "@chakra-ui/react";
import { useState } from "react";
import { DataPoint } from "../../../utils/types";
import { AddDataPointModal } from "./AddDataPointModal";

export function AddDataPointButton({
  replaceDataPoint,
  addDataPoint,
}: {
  replaceDataPoint: (uuid: string, dataPoint: DataPoint) => void;
  addDataPoint: (dataPoint: DataPoint) => void;
}) {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const [yearType, setYearType] = useState<"SINGLE" | "RANGE">("SINGLE");

  return (
    <>
      <Button leftIcon={<HamburgerIcon />} colorScheme="blue" onClick={onOpen}>
        Add custom data point
      </Button>
      <AddDataPointModal
        isOpen={isOpen}
        onClose={onClose}
        replaceDataPoint={replaceDataPoint}
        addDataPoint={addDataPoint}
        yearType={yearType}
        setYearType={setYearType}
      />
    </>
  );
}
