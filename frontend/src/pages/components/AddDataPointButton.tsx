import {
  VStack,
  Heading,
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  FormControl,
  FormLabel,
  Input,
  FormHelperText,
  ModalFooter,
  useDisclosure,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Box,
  ButtonGroup,
  Stack,
} from "@chakra-ui/react";
import { useState } from "react";
import { IndicatorDataFields } from "../../utils/constants";
import { useSmallScreen } from "../../utils/hooks";
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
