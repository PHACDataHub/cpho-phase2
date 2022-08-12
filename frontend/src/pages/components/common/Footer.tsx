import { Heading, Image, VStack } from "@chakra-ui/react";

export function Footer(): JSX.Element {
  return (
    <VStack mt="auto" align="flex-end" backgroundColor="gray.100" p={5}>
      <Image maxWidth="200px" width="80%" src="/static/images/canada.svg" />
    </VStack>
  );
}
