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
} from "@chakra-ui/react";

export function AddDataPointButton() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  return (
    <>
      <VStack spacing={5}>
        <Heading>Data Points</Heading>
        <Button size="lg" colorScheme="blue" onClick={onOpen}>
          Add Data Point
        </Button>
      </VStack>
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Modal Title</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl>
              <FormLabel htmlFor="email">Email address</FormLabel>
              <Input id="email" type="email" />
              <FormHelperText>We'll never share your email.</FormHelperText>
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={onClose}>
              Close
            </Button>
            <Button variant="ghost">Secondary Action</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
}
