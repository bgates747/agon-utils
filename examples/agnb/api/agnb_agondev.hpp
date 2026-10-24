#pragma once
// AgonDev MOS submission adapter; no implicit execution or completion query.
#include "agnb_stdio.hpp"
#include <agon/mos.h>
namespace agnb {
inline bool mos_send(void *,const uint8_t *data,uint16_t bytes) {
    mos_puts(reinterpret_cast<const char*>(data),bytes,0);return true;
}
inline Error load_buffers_mos(const char *filename,Workspace &workspace,
                              Completed completed=nullptr,void *context=nullptr) {
    return load_buffers_file(filename,{nullptr,mos_send},workspace,completed,context);
}
} // namespace agnb
