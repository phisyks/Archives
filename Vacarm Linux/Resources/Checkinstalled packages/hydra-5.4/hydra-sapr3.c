#include "hydra-mod.h"
#ifndef LIBSAPR3
void
dummy_sapr3()
{
  printf("\n");
}
#else

#include <saprfc.h>
#include <ctype.h>

/* temporary workaround fix */
const int *__ctype_tolower;
const int *__ctype_toupper;
const int *__ctype_b;

extern void flood();            /* for -lm */

extern char *HYDRA_EXIT;
RFC_ERROR_INFO_EX error_info;

int
start_sapr3(int s, unsigned long int ip, int port, unsigned char options, char *miscptr, FILE * fp)
{
  RFC_HANDLE handle;
  char *empty = "";
  char *login, *pass, buffer[1024];
  char *buf;
  int i;
  struct sockaddr_in targetip;
  int sysnr = port % 100;
  char opts[] = "RFCINI=N RFCTRACE=N BALANCE=N DEBUG=N TRACE=0 ABAP_DEBUG=0";
//  char opts[] = "RFCINI=N RFCTRACE=Y BALANCE=N DEBUG=Y TRACE=Y ABAP_DEBUG=Y";

  if (strlen(login = hydra_get_next_login()) == 0)
    login = empty;
  if (strlen(pass = hydra_get_next_password()) == 0)
    pass = empty;

  if (strlen(login) > 0)
    for (i = 0; i < strlen(login); i++)
      login[i] = (char) toupper(login[i]);
  if (strlen(pass) > 0)
    for (i = 0; i < strlen(pass); i++)
      pass[i] = (char) toupper(pass[i]);

  memset(buffer, 0, sizeof(buffer));
  memset(&error_info, 0, sizeof(error_info));
  memset(&targetip, 0, sizeof(targetip));
  memcpy(&targetip.sin_addr.s_addr, &ip, 4);
  targetip.sin_family = AF_INET;
#ifdef CYGWIN
  buf = inet_ntoa((struct in_addr) targetip.sin_addr);
#else
  buf = malloc(20);
  inet_ntop(AF_INET, &targetip.sin_addr, buf, 20);
#endif

//strcpy(buf, "mvse001");
  snprintf(buffer, sizeof(buffer), "ASHOST=%s SYSNR=%02d CLIENT=%03d USER=\"%s\" PASSWD=\"%s\" LANG=DE %s", buf, sysnr, atoi(miscptr), login, pass, opts);
#ifndef CYGWIN
  free(buf);
#endif

/*
  USER=SAPCPIC PASSWORD=admin
  USER=SAP*    PASSWORD=PASS

  ## do we need these options?
  SAPSYS=3 SNC_MODE=N SAPGUI=N INVISIBLE=N GUIATOPEN=Y NRCALL=00001 CLOSE=N

  ASHOST= //  IP
  SYSNR=  // port - 3200, scale 2
  CLIENT= // miscptr, scale 2
  ABAP_DEBUG=0
  USER=
  PASSWD= 
  LANG=DE
*/
//printf ("DEBUG: %d Connectstring \"%s\"\n",sizeof(error_info),buffer);
  handle = RfcOpenEx(buffer, &error_info);

//printf("DEBUG: handle %d, key %s, message %s\n", handle, error_info.key, error_info.message);

  if (handle <= RFC_HANDLE_NULL)
    return 3;

  if (strstr(error_info.message, "sapgui") != NULL || strlen(error_info.message) == 0) {
    hydra_report_found_host(port, ip, "sapr3", fp);
    hydra_completed_pair_found();
    if (memcmp(hydra_get_next_pair(), &HYDRA_EXIT, sizeof(HYDRA_EXIT)) == 0)
      return 2;
    return 1;
  } else {
    if (strstr(error_info.key, "ERROR_COMMUNICATION") != NULL) {
      /* sysnr does not exist, report as port closed */
      return 3;
    }
    hydra_completed_pair();
    if (memcmp(hydra_get_next_pair(), &HYDRA_EXIT, sizeof(HYDRA_EXIT)) == 0)
      return 2;
  }
  return 1;
}

void
service_sapr3(unsigned long int ip, int sp, unsigned char options, char *miscptr, FILE * fp, int port)
{
  int run = 1, next_run = 1, sock = -1;

  hydra_register_socket(sp);
  if (memcmp(hydra_get_next_pair(), &HYDRA_EXIT, sizeof(HYDRA_EXIT)) == 0)
    return;
  while (1) {
    switch (run) {
    case 1:                    /* connect and service init function */
      next_run = start_sapr3(sock, ip, port, options, miscptr, fp);
      break;
    case 2:
      hydra_child_exit(0);
    case 3:                    /* clean exit */
      fprintf(stderr, "Error: could not connect to target port %d\n", port);
      hydra_child_exit(1);
    case 4:
      hydra_child_exit(2);
    default:
      hydra_report(stderr, "Caught unknown return code, exiting!\n");
      hydra_child_exit(-1);
    }
    run = next_run;
  }
}

#endif
