import { VStack } from "@chakra-ui/react";
import { Wordmark } from "../atoms/Wordmark";

export function Footer(): JSX.Element {
  return (
    <VStack mt="auto" align="flex-end" backgroundColor="gray.100" p={5}>
      <Wordmark textColor="black" variant="color" width="20%" />
    </VStack>
  );
}
