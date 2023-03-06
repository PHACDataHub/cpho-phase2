import { Image, VStack } from "@chakra-ui/react";
import { Wordmark } from "../atoms/Wordmark";

export function Footer(): JSX.Element {
  return (
    <VStack mt="auto" align="flex-end" backgroundColor="gray.100" p={5}>
      <Wordmark width="10%"/>
    </VStack>
  );
}
