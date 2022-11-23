import { HamburgerIcon } from "@chakra-ui/icons";
import { Button, useDisclosure } from "@chakra-ui/react";
import { DataPoint } from "../../../utils/types";
import { AddDataPointModal } from "./AddDataPointModal";

export function AddDataPointButton({
  dataPoints,
  setDataPoints,
}: {
  dataPoints: DataPoint[];
  setDataPoints: (dataPoints: DataPoint[]) => void;
}) {
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <>
      <Button leftIcon={<HamburgerIcon />} colorScheme="blue" onClick={onOpen}>
        Add custom data point
      </Button>
      <AddDataPointModal
        dataPoints={dataPoints}
        setDataPoints={setDataPoints}
        isOpen={isOpen}
        onClose={onClose}
      />
    </>
  );
}
