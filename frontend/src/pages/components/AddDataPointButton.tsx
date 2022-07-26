import { VStack, Heading, Button, useDisclosure } from "@chakra-ui/react";
import { DataPoint } from "../../utils/types";
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
      <VStack spacing={5}>
        <Heading>Data Points</Heading>
        <Button size="lg" colorScheme="blue" onClick={onOpen}>
          Add Data Point
        </Button>
      </VStack>
      <VStack>
        <Heading size="md">Count: {dataPoints.length}</Heading>
        <AddDataPointModal
          dataPoints={dataPoints}
          setDataPoints={setDataPoints}
          isOpen={isOpen}
          onClose={onClose}
        />
      </VStack>
    </>
  );
}
