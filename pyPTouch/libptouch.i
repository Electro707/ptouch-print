%module ptouchSwig

%{
#define SWIG_FILE_WITH_INIT
#include "ptouch.h"
%}

%include "stdint.i"
%include <cpointer.i>
%include "carrays.i"
%array_class(uint8_t, buffer);

struct _pt_tape_info {
	uint8_t mm;		/* Tape width in mm */
	uint16_t px;		/* Printing area in px */
	double margins;		/* default tape margins in mm */
};

typedef enum _pt_page_flags {
	FEED_NONE	= 0x0,
	FEED_SMALL	= 0x08,
	FEED_MEDIUM	= 0x0c,
	FEED_LARGE	= 0x1a,
	AUTO_CUT	= (1 << 6),
	MIRROR		= (1 << 7),
} pt_page_flags;

struct _pt_dev_info {
	int vid;		/* USB vendor ID */
	int pid;		/* USB product ID */
	char *name;
	int max_px;		/* Maximum pixel width that can be printed */
	int dpi;		/* Dots per inch of the printhead */
	//size_t bytes_per_line;
	int flags;
};

struct _ptouch_stat {
	uint8_t printheadmark;	// 0x80
	uint8_t size;		// 0x20
	uint8_t brother_code;	// "B"
	uint8_t series_code;	// "0"
	uint8_t model;
	uint8_t country;	// "0"
	uint16_t reserved_1;
	uint16_t error;		// table 1 and 2
	uint8_t media_width;	// tape width in mm
	uint8_t media_type;	// table 4
	uint8_t ncol;		// 0
	uint8_t fonts;		// 0
	uint8_t jp_fonts;	// 0
	uint8_t mode;
	uint8_t density;	// 0
	uint8_t media_len;	// table length, always 0
	uint8_t status_type;	// table 5
	uint8_t phase_type;
	uint16_t phase_number;	// table 6
	uint8_t notif_number;
	uint8_t exp;		// 0
	uint8_t tape_color;	// table 8
	uint8_t text_color;	// table 9
	uint32_t hw_setting;
	uint16_t reserved_2;
};

struct _ptouch_dev {
	libusb_device_handle *h;
	pt_dev_info devinfo;
	pt_dev_stat status;
	uint16_t tape_width_px;
};

int ptouch_printer_available(void);
int ptouch_open(ptouch_dev *ptdev);
int ptouch_close(ptouch_dev ptdev);
int ptouch_send(ptouch_dev ptdev, uint8_t *data, size_t len);
int ptouch_init(ptouch_dev ptdev);
int ptouch_lf(ptouch_dev ptdev);
int ptouch_ff(ptouch_dev ptdev);
size_t ptouch_get_max_width(ptouch_dev ptdev);
size_t ptouch_get_tape_width(ptouch_dev ptdev);
int ptouch_eject(ptouch_dev ptdev);
int ptouch_getstatus(ptouch_dev ptdev);
int ptouch_read_status(ptouch_dev ptdev, int timeout);
int ptouch_enable_packbits(ptouch_dev ptdev);
int ptouch_info_cmd(ptouch_dev ptdev, int size_x);
int ptouch_rasterstart(ptouch_dev ptdev);
int ptouch_sendraster(ptouch_dev ptdev, uint8_t *data, size_t len);
void ptouch_rawstatus(uint8_t raw[32]);
void ptouch_list_supported();

const char* pt_mediatype(unsigned char media_type);
const char* pt_tapecolor(unsigned char tape_color);
const char* pt_textcolor(unsigned char text_color);

typedef struct _ptouch_dev *ptouch_dev;
typedef struct _ptouch_stat *pt_dev_stat;

%pointer_functions(struct _ptouch_dev, ptouch_devP);
%pointer_functions(ptouch_dev, ptouch_devPP);

%pointer_functions(struct _ptouch_stat, ptouch_statP);

// %rename(ptouch_stat) _ptouch_stat;