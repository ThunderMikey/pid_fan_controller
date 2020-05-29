# Maintainer: thundermikey

pkgname=pid-fan-controller
pkgver=
pkgrel=1
pkgdesc="PID fan controller with Python3"
arch=('any')
url="https://github.com/ThunderMikey/pid_fan_controller"
license=('GPL3')
depends=('python3' 'python-simple-pid')
provides=("$pkgname")
source=('pid_fan_controller.py'
        'set_fan_control_mode.sh'
        'pid-fan-controller.service')
md5sums=(SKIP
         SKIP
         SKIP)

pkgver() {
  printf "0.r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package() {
  echo $pkgdir
  install -m 644 -Dt "$pkgdir/usr/lib/systemd/system/" pid-fan-controller.service
  install -m 755 -Dt "$pkgdir/usr/share/$pkgname/" pid_fan_controller.py set_fan_control_mode.sh
}

# vim:set ts=2 sw=2 et:
