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
} from "@chakra-ui/react";
import { IndicatorDataFields } from "../../utils/constants";
import { useSmallScreen } from "../../utils/hooks";

export function AddDataPointButton() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const smallScreen = useSmallScreen();

  const handleSubmit = () => {};

  return (
    <>
      <VStack spacing={5}>
        <Heading>Data Points</Heading>
        <Button size="lg" colorScheme="blue" onClick={onOpen}>
          Add Data Point
        </Button>
      </VStack>

      <Modal size="2xl" isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add Data Point</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl display="flex" flexWrap="wrap">
              {IndicatorDataFields.map((field) => {
                return (
                  <Box key={field.id} w={smallScreen ? "100%" : "45%"} m={3}>
                    <FormLabel htmlFor={field.id}>{field.name}</FormLabel>
                    {field.type === "text" ? (
                      <Input id={field.id} />
                    ) : (
                      <NumberInput id={field.id} precision={2} step={0.01}>
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    )}
                  </Box>
                );
              })}
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button type="submit" colorScheme="green" mr={3} onClick={onClose}>
              Save
            </Button>
            <Button colorScheme="red" onClick={onClose}>
              Cancel
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
}
