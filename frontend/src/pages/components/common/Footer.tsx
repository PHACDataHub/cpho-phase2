import { Heading, Image, VStack } from "@chakra-ui/react";

export function Footer(): JSX.Element {
    return <VStack align="flex-end" p={5} backgroundColor="gray.100">
        <Image maxWidth="200px" width="80%"  src="canada.svg" />
    </VStack>
}