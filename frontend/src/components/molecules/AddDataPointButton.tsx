import { HamburgerIcon } from "@chakra-ui/icons";
import { Button, useDisclosure } from "@chakra-ui/react";
import { useContext, useState } from "react";
import IndicatorFormContext from "../../utils/context/IndicatorFormContext";
import { AddDataPointModal } from "./AddDataPointModal";

export function AddDataPointButton() {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const [yearType, setYearType] = useState<"SINGLE" | "RANGE">("SINGLE");

  const { replaceDataPoint, addDataPoint } = useContext(IndicatorFormContext);

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
