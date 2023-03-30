import { useColorMode, VStack } from "@chakra-ui/react";
import { Wordmark } from "../atoms/Wordmark";

export function Footer(): JSX.Element {
  const { colorMode } = useColorMode();
  return (
    <VStack mt="auto" align="flex-end" p={5}>
      <Wordmark
        textColor={colorMode === "dark" ? "white" : "black"}
        variant="color"
        width="20%"
      />
    </VStack>
  );
}
