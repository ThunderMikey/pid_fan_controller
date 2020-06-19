# Maintainer: thundermikey

pkgname=pid-fan-controller
pkgver=0.r19.97f67fb
pkgrel=1
pkgdesc="PID fan controller with Python3"
arch=('any')
url="https://github.com/ThunderMikey/pid_fan_controller"
license=('GPL3')
depends=('python3' 'python-simple-pid' 'python-pyaml')
provides=("$pkgname")
source=('pid_fan_controller.py'
        'override_auto_fan_control.py'
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
  install -m 755 -Dt "$pkgdir/usr/share/$pkgname/" pid_fan_controller.py override_auto_fan_control.py
}

# vim:set ts=2 sw=2 et:
