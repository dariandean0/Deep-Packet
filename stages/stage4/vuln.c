/*
 * Stage 4 - Binary Diagnostic Service
 *
 * Vulnerability : stack buffer overflow via gets() in vuln()
 * Target : overwrite saved EIP with address of win()
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* Win condition */
void win(void) {
    puts("\n[+] Access granted. Retrieving classified data...\n");
    fflush(stdout);

    FILE *f = fopen("/srv/stage4/flag.txt", "r");
    if (f) {
        char flag[256];
        if (fgets(flag, sizeof(flag), f)) {
            printf("FLAG: %s\n", flag);
            fflush(stdout);
        }
        fclose(f);
    } else {
        const char *flag = getenv("FLAG");
        if (flag) {
            printf("FLAG: %s\n", flag);
            fflush(stdout);
        } else {
            puts("[-] Flag file missing.");
            fflush(stdout);
        }
    }

    exit(0);
}

/* Vulnerable function */
void vuln(void) {
    char buf[64];

    puts("Enter diagnostic string:");
    fflush(stdout);

    gets(buf);      

    printf("Received: %s\n", buf);
    fflush(stdout);
}

/* Entry point */
int main(void) {
    /* Disable buffering so output reaches the player through socat */
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin,  NULL, _IONBF, 0);

    puts("============================================");
    puts(" Binary Diagnostic Service [INTERNAL]");
    puts("============================================");
    puts("Running memory self-check...");
    fflush(stdout);

    vuln();

    puts("Self-check complete. No anomalies detected.");
    fflush(stdout);
    return 0;
}